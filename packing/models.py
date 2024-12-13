from django.db import models
from django.db.models import Sum, F, DecimalField
from rest_framework.fields import IntegerField

from helpers.models import BaseModel, EXPLANATION, DECIMAL
from main.models import Business
from products.models import Product


class OrderPackage(BaseModel):
    business = models.ForeignKey(Business, related_name='orders', on_delete=models.PROTECT)
    customer = models.ForeignKey('users.User', related_name='orders',
                                 blank=True, null=True, on_delete=models.PROTECT)
    customer_name = models.CharField(max_length=150, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    postal_code = models.CharField(max_length=10, blank=True, null=True)

    is_packaged = models.BooleanField(default=False)
    packing_data_time = models.DateTimeField(blank=True, null=True)

    is_shipped = models.BooleanField(default=False)
    shipping_data_time = models.DateTimeField(blank=True, null=True)

    packing_admin = models.ForeignKey('users.User', related_name='packed_orders',
                                      blank=True, null=True, on_delete=models.PROTECT)

    explanation = EXPLANATION()

    class Meta(BaseModel.Meta):
        verbose_name = 'OrderPackage'
        permission_basename = 'order_package'
        permissions = (
            ('get.affiliate_factor', 'مشاهده بسته سفارش'),
            ('create.affiliate_factor', 'تعریف بسته سفارش'),
            ('update.affiliate_factor', 'ویرایش بسته سفارش'),
            ('delete.affiliate_factor', 'حذف بسته سفارش'),

            ('getOwn.affiliate_factor', 'مشاهده بسته سفارش خود'),
            ('updateOwn.affiliate_factor', 'ویرایش بسته سفارش خود'),
            ('deleteOwn.affiliate_factor', 'حذف بسته سفارش خود'),
        )

    @property
    def products_quantity(self):
        return self.items.all().aggregate(Sum('quantity'))['quantity__sum']

    @property
    def amount_sum(self):
        return self.items.all().annotate(
            amount_sum=Sum((F('amount') * F('quantity')), output_field=DecimalField()),
        ).aggregate(
            Sum('amount_sum'),
        )['amount_sum__sum']


class OrderPackageItem(BaseModel):
    order_package = models.ForeignKey(OrderPackage, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.PROTECT)
    quantity = models.IntegerField(default=1)
    amount = DECIMAL()

    class Meta(BaseModel.Meta):
        verbose_name = 'OrderPackageItem'
        permission_basename = 'order_package_item'
        permissions = (
            ('get.order_package_item', 'مشاهده آیتم بسته سفارش'),
            ('create.order_package_item', 'تعریف آیتم بسته سفارش'),
            ('update.order_package_item', 'ویرایش آیتم بسته سفارش'),
            ('delete.order_package_item', 'حذف آیتم بسته سفارش'),

            ('getOwn.order_package_item', 'مشاهده آیتم بسته سفارش خود'),
            ('updateOwn.order_package_item', 'ویرایش آیتم بسته سفارش خود'),
            ('deleteOwn.order_package_item', 'حذف آیتم بسته سفارش خود'),
        )

    @property
    def amount_sum(self):
        return round(self.amount) * self.quantity