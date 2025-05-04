import datetime

from django.core.exceptions import ValidationError
from django.db import models
from django_fsm import FSMField, transition

from helpers.models import DECIMAL


class Wallet(models.Model):
    user = models.OneToOneField('users.User', on_delete=models.CASCADE, related_name='wallet',
                                blank=True, null=True)
    business = models.OneToOneField('main.Business', on_delete=models.CASCADE, related_name='wallet',
                                    blank=True, null=True)
    balance = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        super().clean()
        if not self.user and not self.business:
            raise ValidationError("حداقل یکی از فیلدهای 'کاربر' یا 'کسب و کار' باید مقدار داشته باشد.")


class Transaction(models.Model):
    TOP_UP = 'top-up'
    WITHDRAW = 'withdraw'
    TRANSFER = 'transfer'
    PAYMENT = 'payment'
    INVESTMENT = 'investment'

    TRANSACTION_TYPE = (
        (TOP_UP, 'شارژ ولت'),
        (WITHDRAW, 'برداشت'),
        (TRANSFER, 'انتقال'),
        (PAYMENT, 'پرداخت'),
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
    status = models.CharField(max_length=10, choices=TRANSACTION_STATUS, default='PENDING')
    description = models.TextField(blank=True, null=True)
    metadata = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    transaction_for = models.CharField(max_length=10, choices=TRANSACTION_STATUS, default='PENDING')


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


class AuditAction(models.TextChoices):
    TOP_UP_REQUESTED = "wallet_top_up_requested", "Top-up Requested"
    TOP_UP_SUCCESS = "wallet_top_up_success", "Top-up Success"
    WITHDRAW_REQUESTED = "wallet_withdraw_wallet_request", "Wallet Withdrawal Requested"
    WITHDRAW_SUCCESS = "wallet_withdraw_wallet__success", "Wallet Withdraw Success"
    TRANSFER = "wallet_transfer", "Wallet Transfer"
    PAYMENT_ORDER = "wallet_payment_order", "Payment for Order"
    INVESTMENT = "wallet_investment", "Investment Made"
    BALANCE_UPDATED = "wallet_balance_updated", "Balance Updated"
    TRANSACTION_FAILED = "transaction_failed", "Transaction Failed"
    MANUAL_ADJUSTMENT = "admin_manual_adjustment", "Manual Adjustment"


class AuditSeverity(models.TextChoices):
    INFO = "info", "Info"
    WARNING = "warning", "Warning"
    CRITICAL = "critical", "Critical"


class FinancialAuditLog(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='pay_logs')
    receiver = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='receive_logs')
    transaction = models.ForeignKey(Transaction, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=50, choices=AuditAction.choices)
    severity = models.CharField(max_length=10, choices=AuditSeverity.choices, default=AuditSeverity.INFO)
    ip_address = models.GenericIPAddressField()
    user_agent = models.CharField(max_length=256)
    extra_info = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


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
    gateway = models.CharField(max_length=30, blank=True, null=True)
    reference_id = models.CharField(max_length=100, blank=True, null=True, unique=True)
    created_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    paid_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return "پرداخت {} {}".format(self.reference_id, self.user.name)

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
