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
    customer = models.ForeignKey('users.User', related_name='affiliate_factors_as_customer',
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

    @property
    def title(self):
        return 'فاکتور فروش در افیلیت به ' + self.customer_name + ' با شماره تماس ' + self.phone


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
