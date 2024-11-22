import datetime
from decimal import Decimal

import zeep
from django.db import models
from django.db.models import JSONField, F, Q
from django.db.models.functions import Least, Round, TruncMinute, Cast
from django.db.models.aggregates import Max
from rest_framework.exceptions import ValidationError

from affiliate.models import AffiliateFactor
from main.models import Business
from server.configs import PEC

from helpers.functions import get_current_user, sanad_exp
from helpers.models import BaseModel, DECIMAL, EXPLANATION
from helpers.serializers import validate_required_fields
from server.settings import DEVELOPING

TAX = Decimal(0.1)


class DiscountCode(BaseModel):
    code = models.CharField(max_length=31, unique=True)

    users = models.ManyToManyField('users.User', null=True, blank=True)
    start_at = models.DateTimeField(null=True, blank=True)
    expire_at = models.DateTimeField(null=True, blank=True)

    max_discount_amount = DECIMAL()
    discount_percentage = models.IntegerField(null=True, blank=True)

    usage = models.IntegerField(default=0)
    usage_limit = models.IntegerField(null=True, blank=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        _is_verified = False
        _factor = None

    class Meta(BaseModel.Meta):
        pass

    def verify(self):
        user = get_current_user()

        if self.start_at and self.start_at < datetime.datetime.now():
            raise ValidationError("زمان استفاده از کد تخفیف هنوز آغاز نشده است")

        if self.expire_at and self.expire_at > datetime.datetime.now():
            raise ValidationError("کد تخفیف منقضی شده است")

        if self.usage_limit and self.usage >= self.usage_limit:
            raise ValidationError("ظرفیت کد تخفیف تکمیل شده است")

        if self.users.count() > 0:
            user = get_current_user()
            if user not in self.users.all():
                raise ValidationError("کد تخفیف معتبر نمی باشد")

        if Factor.objects.filter(is_paid=False, discount_code=self, user=user).exists():
            raise ValidationError("کد تخفیف استفاده شده است")

        return True

    def get_discount_amount(self, factor_amount):
        discount_amount = factor_amount * self.discount_percentage / 100
        discount_amount = min(discount_amount, self.max_discount_amount)
        return discount_amount

    def apply(self, factor):
        assert self.verify()

        factor.discount_code = self
        factor.discount_amount = self.get_discount_amount(factor.amount)
        factor.save()

    def use(self):
        assert self.verify()
        self.usage += 1
        self.save()


class FactorManager(models.Manager):
    def get_queryset(self):
        qs = super().get_queryset().annotate(
            after_discount_amount=Round(F('amount') - Least('discount_amount', 'amount')),
            added_value_tax=Round((F('amount') - Least('discount_amount', 'amount')) * TAX),
            payable_amount=Round((F('amount') - Least('discount_amount', 'amount')) * (Decimal(1) + TAX)),
            time=TruncMinute('created_at__time'),
        )
        return qs


class Factor(BaseModel):
    user = models.ForeignKey('users.User', on_delete=models.PROTECT)
    business = models.ForeignKey(Business, on_delete=models.PROTECT, null=True, blank=True)
    is_paid = models.BooleanField(default=False)
    amount = DECIMAL()

    # to store company name temporary
    company_name = models.CharField(max_length=150, null=True, blank=True)

    discount_code = models.ForeignKey(DiscountCode, on_delete=models.PROTECT, null=True, blank=True)
    discount_amount = DECIMAL(default=0)

    class Meta(BaseModel.Meta):
        pass

    objects = FactorManager()

    @property
    def value_added_tax(self):
        return max(self.amount - self.discount_amount, Decimal(0)) * TAX

    @property
    def final_amount(self):
        return max(self.amount - self.discount_amount, Decimal(0)) + self.value_added_tax

    def update_amounts(self):
        amount = 0
        for item in self.items.all():
            amount += item.update_amount(save=True)
        self.amount = amount
        self.save()

    def get_payable_amount(self):
        return max(Decimal(self.amount - self.discount_amount), Decimal(0)) * (Decimal(1) + TAX)  # read tax from configs

    def pay(self):
        assert not self.is_paid

        discount_code = self.discount_code
        if discount_code:
            discount_code.use()

        self.update_amounts()

        # create withdraw transaction
        transaction = Transaction.create_transaction(
            Transaction.WITHDRAW,
            self.user,
            self.get_payable_amount(),
            self
        )
        transaction.success()

        self.is_paid = True
        self.save()


class FactorItem(BaseModel):
    CUSTOMER_AFFILIATE_FACTOR = 'af'
    OTHER = 'o'

    TYPES = (
        (CUSTOMER_AFFILIATE_FACTOR, 'فروش در افیلیت'),
        (OTHER, 'سایر')
    )

    factor = models.ForeignKey(Factor, related_name='items', on_delete=models.CASCADE)
    type = models.CharField(max_length=2, choices=TYPES)

    affiliate_factor = models.ForeignKey(AffiliateFactor, related_name='affiliate_factor_items',
                                         on_delete=models.CASCADE, null=True, blank=True)

    amount = DECIMAL()

    explanation = EXPLANATION()

    class Meta(BaseModel.Meta):
        ordering = ['pk']

    def update_amount(self, save):
        assert not self.factor.is_paid
        if self.type == self.CUSTOMER_AFFILIATE_FACTOR:
            self.amount = self.affiliate_factor.factor_price_sum

        elif self.type == self.OTHER:
            pass
        else:
            raise Exception("Invalid FactorItem type")

        if save:
            self.save(update_amount=False)

        return self.amount

    def save(self, update_amount=True, *args, **kwargs) -> None:
        if update_amount:
            self.update_amount(False)

        super().save(*args, **kwargs)


class Wallet(BaseModel):
    balance = DECIMAL(default=0)

    class Meta(BaseModel.Meta):
        pass

    def deposit(self, amount):
        self.balance += Decimal(amount)
        self.save()

    def withdraw(self, amount):
        if self.balance < amount:
            raise ValidationError("موجودی کیف پول کافی نمی باشد")
        self.balance -= Decimal(amount)
        self.save()

    def save(self, *args, **kwargs) -> None:
        if self.balance < 0:
            raise ValueError("Negative wallet balance")

        super().save(*args, **kwargs)

    def __str__(self):
        user = self.user_set.first()
        if user:
            return f"{user.username} ({self.id})"
        return str(self.id)


class Transaction(BaseModel):
    DEPOSIT = 'd'
    WITHDRAW = 'w'

    TYPES = (
        (DEPOSIT, 'واریز'),
        (WITHDRAW, 'برداشت'),
    )

    type = models.CharField(max_length=1, choices=TYPES)

    # payer or receiver
    user = models.ForeignKey('users.User', on_delete=models.PROTECT)

    wallet = models.ForeignKey(Wallet, on_delete=models.PROTECT)

    amount = DECIMAL()  # todo remove amount field

    bed = DECIMAL()
    bes = DECIMAL()

    datetime = models.DateTimeField()

    # this factor will pay if transaction was successful
    factor = models.ForeignKey(Factor, on_delete=models.PROTECT, null=True, blank=True)

    _is_successful = models.BooleanField(default=False)

    # + other gateway fields
    _order_id = models.BigIntegerField(null=True, blank=True)

    _gateway_callback = JSONField(null=True, blank=True)
    """
        Example:
        {
            "Token": "218072956457997",
            "OrderId": "21",
            "TerminalNo": "98826118",
            "RRN": "735373431081",
            "status": "0",
            "HashCardNumber": "2291EC7CCC5AA9AACBB86C17F652137B472AD582C38E8BA4976D397D6B2BA7FB",
            "Amount": "1,000",
            "SwAmount": "",
            "STraceNo": "65424",
            "DiscoutedProduct": ""
        }
    """

    explanation = EXPLANATION()

    class Meta(BaseModel.Meta):
        pass

    def __str__(self):
        return "{} - {} ({})".format(self.get_type_display(), self.user.name, self.id)

    def success(self):
        if self._is_successful:
            raise Exception("Transaction is already successful")

        self._is_successful = True
        self.save()

        if self.type == self.DEPOSIT:
            self.wallet.deposit(self.amount)
            if self.factor:
                self.factor.pay()
        elif self.type == self.WITHDRAW:
            self.wallet.withdraw(self.amount)
        else:
            raise Exception("Invalid transaction type")

        if self.type == self.DEPOSIT:
            if self._order_id:
                explanation = sanad_exp(
                    "شارژ حساب به شماره پیگیری",
                    self._order_id,
                    "مورخ",
                    self.datetime,
                    "از طریق درگاه",
                    "پارسیان"
                )
            else:
                explanation = sanad_exp(
                    "هدیه شارژ کیف پول مورخ",
                    self.datetime,
                )
        else:
            if self.factor:
                if self.factor.items.filter(type=FactorItem.CUSTOMER_AFFILIATE_FACTOR).exists():
                    explanation = "پرداخت فاکتور افیلیت"
                else:
                    explanation = "برداشت از حساب"

                explanation = sanad_exp(
                    explanation,
                    "به شماره فاکتور",
                    self.factor.id,
                    "مورخ",
                    self.datetime
                )
            else:
                explanation = sanad_exp(
                    "برگشت وجه شارژ شده به حساب مورخ",
                    self.datetime
                )

        self.explanation = explanation
        self.save()

    @staticmethod
    def create_transaction(transaction_type, user, amount, factor):
        bed = bes = 0
        if transaction_type == Transaction.DEPOSIT:
            bed = amount
        else:
            bes = amount

        transaction = Transaction(
            type=transaction_type,
            user=user,
            wallet=user.get_wallet(),
            amount=amount,
            bed=bed,
            bes=bes,
            datetime=datetime.datetime.now(),
            factor=factor
        )
        transaction.save()
        transaction.refresh_from_db()
        return transaction

    @staticmethod
    def get_redirect_url(transaction):

        order_id = (Transaction.objects.aggregate(Max('_order_id'))['_order_id__max'] or 0) + 1

        if DEVELOPING:
            transaction._order_id = order_id
            transaction.success()
            if transaction.factor:
                return f'http://localhost:8080/panel/subscriptionFactorForm/{transaction.factor_id}?success=true'
            else:
                return f'http://localhost:8080/panel/wallet'

        phone = transaction.user.phone
        if not phone.startswith('98'):  # 0917..., 917...
            if phone.startswith('0'):
                phone = '98' + phone[1:]
            else:
                phone = '98' + phone

        while True:
            data = {
                "LoginAccount": PEC['PIN_CODE'],
                "Amount": int(transaction.amount),
                "OrderId": order_id,
                "CallBackUrl": "http://localhost:8080/subscriptions/callback",
                "Originator": phone
            }
            client = zeep.Client("https://pec.shaparak.ir/NewIPGServices/Sale/SaleService.asmx?WSDL")
            res = client.service.SalePaymentRequest(data)
            status = res['Status']
            if status == 0:
                transaction._order_id = order_id
                transaction.save()
                return f"https://pec.shaparak.ir/NewIPG/?token={res['Token']}"
            elif status == -112:
                # duplicate order id
                order_id += 1
                continue


