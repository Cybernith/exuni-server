import datetime
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum, F, DecimalField, Max
import zeep

from helpers.models import BaseModel, DECIMAL, EXPLANATION
from main.models import Business
from products.models import Product
from server.configs import PEC
from server.settings import DEVELOPING
from users.models import User


class AffiliateFactor(BaseModel):
    INITIAL_REGISTRATION_STAGE = 'irs'
    IN_PROCESSING = 'ipr'
    IN_PACKING = 'ipa'
    SHIPPED = 'shp'

    STATUSES = (
        (INITIAL_REGISTRATION_STAGE, 'ثبت اولیه'),
        (IN_PROCESSING, 'درحال پردازش'),
        (IN_PACKING, 'در حال بسته بندی'),
        (SHIPPED, 'ارسال شده'),
    )

    status = models.CharField(max_length=3, choices=STATUSES, default=INITIAL_REGISTRATION_STAGE)
    business = models.ForeignKey(Business, related_name='affiliate_factors', blank=True, null=True,
                                 on_delete=models.PROTECT)
    customer = models.ForeignKey(User, related_name='affiliate_factors_as_customer',
                                 blank=True, null=True, on_delete=models.PROTECT)
    customer_name = models.CharField(max_length=150, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    postal_code = models.CharField(max_length=10, blank=True, null=True)
    is_paid = models.BooleanField(default=False)

    class Meta(BaseModel.Meta):
        verbose_name = 'AffiliateFactor'
        permission_basename = 'affiliate_factor'
        permissions = (
            ('get.affiliate_factor', 'مشاهده فاکتور افیلیت'),
            ('create.affiliate_factor', 'تعریف فاکتور افیلیت'),
            ('update.affiliate_factor', 'ویرایش فاکتور افیلیت'),
            ('delete.affiliate_factor', 'حذف فاکتور افیلیت'),

            ('getOwn.affiliate_factor', 'مشاهده فاکتور افیلیت خود'),
            ('updateOwn.affiliate_factor', 'ویرایش فاکتور افیلیت خود'),
            ('deleteOwn.affiliate_factor', 'حذف فاکتور افیلیت خود'),
        )

    @property
    def factor_price_sum(self):
        items = self.items.all().annotate(
            final_price=Sum(F('quantity') * F('price'), output_field=DecimalField()),
        ).aggregate(Sum('final_price'))
        return items['final_price__sum']


class AffiliateFactorItem(BaseModel):
    affiliate_factor = models.ForeignKey(AffiliateFactor, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='affiliate_factor_items',  on_delete=models.PROTECT)
    quantity = models.IntegerField(default=1)
    price = DECIMAL()

    class Meta(BaseModel.Meta):
        verbose_name = 'AffiliateFactorItem'
        permission_basename = 'affiliate_factor_item'
        permissions = (
            ('get.affiliate_factor_item', 'مشاهده ردیف فاکتور افیلیت'),
            ('create.affiliate_factor_item', 'تعریف ردیف فاکتور افیلیت'),
            ('update.affiliate_factor_item', 'ویرایش ردیف فاکتور افیلیت'),
            ('delete.affiliate_factor_item', 'حذف ردیف فاکتور افیلیت'),

            ('getOwn.affiliate_factor_item', 'مشاهده ردیف فاکتور افیلیت خود'),
            ('updateOwn.affiliate_factor_item', 'ویرایش ردیف فاکتور افیلیت خود'),
            ('deleteOwn.affiliate_factor_item', 'حذف ردیف فاکتور افیلیت خود'),
        )


class PaymentInvoice(BaseModel):
    business = models.ForeignKey(Business, related_name='payment_invoices', on_delete=models.PROTECT)
    payment_data_time = models.DateTimeField(default=datetime.datetime.now())
    is_paid = models.BooleanField(default=False)
    amount = DECIMAL(default=0)

    description = EXPLANATION()

    class Meta(BaseModel.Meta):
        verbose_name = 'PaymentInvoice'
        permission_basename = 'payment_invoice'
        permissions = (
            ('get.payment_invoice', 'مشاهده فاکتور پرداخت'),
            ('create.payment_invoice', 'تعریف فاکتور پرداخت'),
            ('update.payment_invoice', 'ویرایش فاکتور پرداخت'),
            ('delete.payment_invoice', 'حذف فاکتور پرداخت'),

            ('getOwn.payment_invoice', 'مشاهده فاکتور پرداخت خود'),
            ('updateOwn.payment_invoice', 'ویرایش فاکتور پرداخت خود'),
            ('deleteOwn.payment_invoice', 'حذف فاکتور پرداخت خود'),
        )

    @property
    def calculate_amount(self):
        amount = 0
        for item in self.items.all():
            amount += item.amount
        return amount

    def set_amount(self):
        self.amount = self.calculate_amount
        self.save()

    def pay(self):
        assert not self.is_paid
        self.is_paid = True
        self.save()


class PaymentInvoiceItem(BaseModel):
    CUSTOMER_AFFILIATE_FACTOR = 'caf'

    TYPES = (
        (CUSTOMER_AFFILIATE_FACTOR, 'فاکتور مشتری افیلیت'),
    )

    payment_invoice = models.ForeignKey(PaymentInvoice, related_name='items', on_delete=models.CASCADE)
    type = models.CharField(max_length=3, choices=TYPES)
    affiliate_factor = models.ForeignKey(AffiliateFactor, related_name='payment_invoice',
                                         on_delete=models.PROTECT, blank=True, null=True)

    amount = DECIMAL()
    description = EXPLANATION()

    @property
    def name(self):
        return self.get_type_display() + ' ' + self.affiliate_factor.customer_name

    class Meta(BaseModel.Meta):
        verbose_name = 'PaymentInvoiceItem'
        permission_basename = 'payment_invoice_item'
        permissions = (
            ('get.payment_invoice_item', 'مشاهده ردیف فاکتور پرداخت '),
            ('create.payment_invoice_item', 'تعریف ردیف فاکتور پرداخت'),
            ('update.payment_invoice_item', 'ویرایش ردیف فاکتور پرداخت'),
            ('delete.payment_invoice_item', 'حذف ردیف فاکتور پرداخت'),

            ('getOwn.payment_invoice_item', 'مشاهده ردیف فاکتور پرداخت خود'),
            ('updateOwn.payment_invoice_item', 'ویرایش ردیف فاکتور پرداخت خود'),
            ('deleteOwn.payment_invoice_item', 'حذف ردیف فاکتور پرداخت خود'),
        )


class Wallet(BaseModel):
    business = models.OneToOneField(Business, related_name='wallet', on_delete=models.PROTECT)
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
        return str(self.id)


class Transaction(BaseModel):
    DEPOSIT = 'd'
    WITHDRAW = 'w'
    PAYMENT = 'p'

    TYPES = (
        (DEPOSIT, 'واریز'),
        (WITHDRAW, 'برداشت'),
        (PAYMENT, 'پرداخت'),
    )

    type = models.CharField(max_length=1, choices=TYPES)

    wallet = models.ForeignKey(Wallet, on_delete=models.PROTECT, null=True, blank=True)

    amount = DECIMAL()

    bed = DECIMAL()
    bes = DECIMAL()

    datetime = models.DateTimeField()

    # this factor will pay if transaction was successful and transaction type is PAYMENT
    payment_invoice = models.ForeignKey(PaymentInvoice, on_delete=models.PROTECT, null=True, blank=True)

    _is_successful = models.BooleanField(default=False)

    # + other gateway fields
    _order_id = models.BigIntegerField(null=True, blank=True)

    _gateway_callback = models.JSONField(null=True, blank=True)
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
        if self.type == self.PAYMENT:
            return "{} - {} ({})".format(self.get_type_display(), self.payment_invoice.business.name, self.id)
        else:
            return "{} - {} ({})".format(self.get_type_display(), self.wallet.business.name, self.id)

    def success(self):
        if self._is_successful:
            raise Exception("Transaction is already successful")

        self._is_successful = True
        self.save()

        if self.type == self.DEPOSIT:
            self.wallet.deposit(self.amount)
        elif self.type == self.WITHDRAW:
            self.wallet.withdraw(self.amount)
            self.payment_invoice.pay()
        elif self.type == self.PAYMENT:
            self.payment_invoice.pay()

        else:
            raise Exception("Invalid transaction type")

    @staticmethod
    def create_transaction(transaction_type, business, amount, payment_invoice, wallet):
        bed = bes = 0
        if transaction_type == Transaction.DEPOSIT:
            bed = amount
        else:
            bes = amount

        transaction = Transaction(
            type=transaction_type,
            business=business,
            wallet=wallet,
            amount=amount,
            bed=bed,
            bes=bes,
            datetime=datetime.datetime.now(),
            payment_invoice=payment_invoice
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
            if transaction.payment_invoice:
                return f'http://localhost:8080/panel/subscriptionFactorForm/{transaction.payment_invoice.id}?success=true'
            else:
                return f'http://localhost:8080/panel/wallet'

        phone = transaction.payment_invoice.business.admin.phone
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
                "CallBackUrl": "https://api.app.sobhan.net/subscriptions/callback",
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


