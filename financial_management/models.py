import datetime
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models, transaction as db_transaction
from django.db.models import UniqueConstraint, Q
from django.utils import timezone
from django_fsm import FSMField, transition

from helpers.models import DECIMAL


class Wallet(models.Model):
    user = models.OneToOneField('users.User', on_delete=models.CASCADE, related_name='exuni_wallet',
                                blank=True, null=True)
    business = models.OneToOneField('main.Business', on_delete=models.CASCADE, related_name='exuni_wallet',
                                    blank=True, null=True)
    balance = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        super().clean()
        if not self.user and not self.business:
            raise ValidationError("حداقل یکی از فیلدهای 'کاربر' یا 'کسب و کار' باید مقدار داشته باشد.")

    def reduce_balance(self, amount: Decimal, description: str = 'خرید از کیف پول', transaction_type=None, **kwargs):
        if amount <= 0:
            raise ValidationError('مقدار برداشت باید یک عدد مثبت باشد.')

        with db_transaction.atomic():
            wallet = Wallet.objects.select_for_update().get(pk=self.pk)

            if wallet.balance < amount:
                raise ValidationError('موجودی کافی نیست.')

            balance_before = wallet.balance
            wallet.balance -= amount
            wallet.save()

            WalletLedger.objects.create(
                wallet=wallet,
                amount=amount,
                balance_before=balance_before,
                balance_after=wallet.balance,
                is_credit=False,
                description=description
            )

            Transaction.objects.create(
                wallet=wallet,
                amount=amount,
                type=transaction_type or Transaction.BUY,
                status=Transaction.SUCCESS,
                **kwargs
            )

    def increase_balance(self, amount: Decimal, description: str = 'شارژ کیف پول', transaction_type=None, **kwargs):
        if amount <= 0:
            raise ValidationError('مقدار برداشت باید یک عدد مثبت باشد.')

        with db_transaction.atomic():
            wallet = Wallet.objects.select_for_update().get(pk=self.pk)
            wallet.balance += amount
            wallet.save()


class Transaction(models.Model):
    TOP_UP = 'top-up'
    WITHDRAW = 'withdraw'
    TRANSFER = 'transfer'
    PAYMENT = 'payment'
    INVESTMENT = 'investment'
    BUY = 'buy'

    TRANSACTION_TYPE = (
        (TOP_UP, 'شارژ ولت'),
        (WITHDRAW, 'برداشت'),
        (PAYMENT, 'پرداخت'),
        (BUY, 'خرید از ولت'),
        (TRANSFER, 'انتقال'),
        (INVESTMENT, 'سرمایه گذاری'),
    )

    PENDING = 'pending'
    SUCCESS = 'success'
    FAILED = 'failed'

    TRANSACTION_STATUS = (
        (PENDING, 'بلاتکلیف'),
        (SUCCESS, 'موفق'),
        (FAILED, 'ناموفق'),
    )

    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    type = models.CharField(max_length=20, choices=TRANSACTION_TYPE)
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    status = models.CharField(max_length=10, choices=TRANSACTION_STATUS, default=PENDING)
    description = models.TextField(blank=True, null=True)
    metadata = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    transaction_for = models.CharField(max_length=10, choices=TRANSACTION_TYPE, default=WITHDRAW)


class WalletLedger(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='ledgers')
    transaction = models.ForeignKey(Transaction, on_delete=models.SET_NULL, null=True, blank=True)

    amount = models.DecimalField(max_digits=20, decimal_places=2)
    balance_before = models.DecimalField(max_digits=20, decimal_places=2)
    balance_after = models.DecimalField(max_digits=20, decimal_places=2)
    is_credit = models.BooleanField()

    description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class BankAccount(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='bank_accounts')
    business = models.ForeignKey('main.Business', on_delete=models.CASCADE, related_name='bank_accounts',
                                 blank=True, null=True)

    bank_name = models.CharField(max_length=100)
    iban = models.CharField(max_length=26)
    card_number = models.CharField(max_length=16)
    is_verified = models.BooleanField(default=False)

    def clean(self):
        super().clean()
        if not self.user and not self.business:
            raise ValidationError("حداقل یکی از فیلدهای 'کاربر' یا 'کسب و کار' باید مقدار داشته باشد.")


class Payment(models.Model):
    INITIATED = 'in'
    PENDING = 'pe'
    SUCCESS = 'su'
    FAILED = 'fa'
    EXPIRED = 'ex'

    STATUS_CHOICES = (
        (INITIATED, 'شروع شده'),
        (PENDING, 'در حال انجام'),
        (SUCCESS, 'موفق'),
        (FAILED, 'ناموفق'),
        (EXPIRED, 'منقضی  شده'),
    )

    FOR_SHOP_ORDER = 'fso'
    FOR_AFFILIATE_ORDERS = 'fao'
    FOR_TOP_UP_WALLET = 'ftw'

    PAYMENT_TYPE_CHOICES = (
        (FOR_SHOP_ORDER, 'سفارش فروشگاه'),
        (FOR_AFFILIATE_ORDERS, 'سفارش های افیلیت'),
        (FOR_TOP_UP_WALLET, 'شارژ ولت'),
    )
    type = models.CharField(choices=PAYMENT_TYPE_CHOICES, default=FOR_SHOP_ORDER, max_length=3)

    shop_order = models.OneToOneField('shop.ShopOrder', related_name='bank_payment', on_delete=models.CASCADE,
                                      blank=True, null=True, unique=True)

    user = models.ForeignKey('users.User', related_name='bank_payment', on_delete=models.CASCADE)
    business = models.ForeignKey('main.Business', related_name='bank_payment', on_delete=models.CASCADE, null=True)

    status = FSMField(choices=STATUS_CHOICES, default=INITIATED, protected=False)
    amount = DECIMAL()
    used_amount_from_wallet = DECIMAL()
    gateway = models.CharField(max_length=30, blank=True, null=True)
    reference_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    paid_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        constraints = [
            UniqueConstraint(fields=['reference_id'], name='unique_reference_id',
                             condition=Q(reference_id__isnull=False))
        ]
    def __str__(self):
        return f"پرداخت {self.reference_id or 'بدون شناسه'} توسط {self.user.name}"

    @transition(field='status', source=INITIATED, target=PENDING)
    def mark_as_pending(self, user=None):
        print(f'{user} pending')
        self.status = self.PENDING
        self.save()

    @transition(field='status', source=PENDING, target=SUCCESS)
    def mark_as_success_payment(self, user=None):
        self.paid_at = datetime.datetime.now()
        self.status = self.SUCCESS
        self.save()
        # verify transaction from bank api
        print(f'{user} payment successfully done')

    @transition(field='status', source=PENDING, target=FAILED)
    def mark_as_failed_payment(self, user=None):
        self.status = self.FAILED
        self.save()
        print(f'{user} payment failed')

    @transition(field='status', source=PENDING, target=EXPIRED)
    def mark_as_expired_payment(self, user=None):
        self.status = self.EXPIRED
        self.save()
        print(f'{user} payment expired')


class AffiliateOrderPayment(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='affiliate_orders')
    order = models.ForeignKey('affiliate.AffiliateFactor', on_delete=models.CASCADE, related_name='payment')

    class Meta:
        unique_together = ('payment', 'order')


class AuditAction(models.TextChoices):
    TOP_UP_REQUESTED = "wallet_top_up_requested", "Top-up Requested"
    TOP_UP_SUCCESS = "wallet_top_up_success", "Top-up Success"
    WITHDRAW_REQUESTED = "wallet_withdraw_wallet_request", "Wallet Withdrawal Requested"
    WITHDRAW_SUCCESS = "wallet_withdraw_wallet__success", "Wallet Withdraw Success"
    TRANSFER = "wallet_transfer", "Wallet Transfer"
    PAYMENT_ORDER = "payment_order", "Payment for Order"
    INVESTMENT = "wallet_investment", "Investment Made"
    BALANCE_UPDATED = "wallet_balance_updated", "Balance Updated"
    TRANSACTION_FAILED = "transaction_failed", "Transaction Failed"
    PAYMENT_FAILED = "payment_failed", "Payment Failed"
    MANUAL_ADJUSTMENT = "admin_manual_adjustment", "Manual Adjustment"


class AuditSeverity(models.TextChoices):
    INFO = "info", "Info"
    WARNING = "warning", "Warning"
    CRITICAL = "critical", "Critical"


class FinancialAuditLog(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='pay_logs')
    receiver = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='receive_logs')
    transaction = models.ForeignKey(Transaction, on_delete=models.SET_NULL, null=True, blank=True)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=50, choices=AuditAction.choices)
    severity = models.CharField(max_length=10, choices=AuditSeverity.choices, default=AuditSeverity.INFO)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.CharField(max_length=256, blank=True, null=True)
    extra_info = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Discount(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def is_valid(self):
        now = timezone.now()
        return (
                self.is_active and
                (self.start_date is None or self.start_date <= now) and
                (self.end_date is None or now <= self.end_date)
        )


class DiscountCondition(models.Model):
    CATEGORY = 'category'
    BRAND = 'brand'
    PRODUCT = 'product'
    PRICE_OVER = 'price_over'
    PRICE_LIMIT = 'price_limit'
    USER = 'user'

    CONDITION_TYPES = (
        (CATEGORY, 'دسته بندی'),
        (BRAND, 'برند'),
        (PRODUCT, 'کالا'),
        (PRICE_OVER, 'از قیمت'),
        (PRICE_LIMIT, 'تا قیمت'),
        (USER, 'کاربر'),
    )

    discount = models.ForeignKey(Discount, on_delete=models.CASCADE, related_name='conditions')
    type = models.CharField(max_length=20, choices=CONDITION_TYPES)

    def __str__(self):
        return f"{self.discount.name} - {self.get_type_display()}"


class DiscountConditionCategory(models.Model):
    condition = models.OneToOneField(DiscountCondition, on_delete=models.CASCADE, related_name='category_condition')
    categories = models.ManyToManyField('products.Category')


class DiscountConditionProduct(models.Model):
    condition = models.OneToOneField(DiscountCondition, on_delete=models.CASCADE, related_name='product_condition')
    products = models.ManyToManyField('products.Product')


class DiscountConditionUser(models.Model):
    condition = models.OneToOneField(DiscountCondition, on_delete=models.CASCADE, related_name='user_condition')
    users = models.ManyToManyField('users.User')


class DiscountConditionBrand(models.Model):
    condition = models.OneToOneField(DiscountCondition, on_delete=models.CASCADE, related_name='brand_condition')
    brands = models.ManyToManyField('products.Brand')


class DiscountConditionPriceOver(models.Model):
    condition = models.OneToOneField(DiscountCondition, on_delete=models.CASCADE, related_name='price_over_condition')
    price_over = models.DecimalField(max_digits=12, decimal_places=2)


class DiscountConditionPriceLimit(models.Model):
    condition = models.OneToOneField(DiscountCondition, on_delete=models.CASCADE, related_name='price_limit_condition')
    price_limit = models.DecimalField(max_digits=12, decimal_places=2)


class DiscountAction(models.Model):
    PERCENTAGE = 'percentage'
    FIXED = 'fixed_amount'
    FREE_SHIPPING = 'free_shipping'

    ACTION_TYPES = (
        (PERCENTAGE, 'درصد'),
        (FIXED, 'مبلغ'),
        (FREE_SHIPPING, 'ارسال رایگان'),
    )

    discount = models.OneToOneField(Discount, on_delete=models.CASCADE, related_name='action')
    type = models.CharField(max_length=20, choices=ACTION_TYPES)
    value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.discount.name} - {self.value}{self.get_type_display()}"


class DiscountUsage(models.Model):
    discount = models.ForeignKey(Discount, on_delete=models.CASCADE)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    used_at = models.DateTimeField(auto_now_add=True)
