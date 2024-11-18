from django.db import models

from helpers.models import BaseModel, DECIMAL
from main.models import Business
from products.models import Product
from users.models import User


class AffiliateFactor(BaseModel):
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

            ('getOwn.affiliate_factor', 'مشاهده ردیف فاکتور افیلیت خود'),
            ('updateOwn.affiliate_factor', 'ویرایش ردیف فاکتور افیلیت خود'),
            ('deleteOwn.affiliate_factor', 'حذف ردیف فاکتور افیلیت خود'),
        )

