from django.db import models

from helpers.functions import add_separator
from helpers.models import BaseModel, DECIMAL
from colorfield.fields import ColorField
import os
import binascii

def custom_upload_to(instance, filename):
    return 'images/{filename}'.format(filename=filename)


class Business(BaseModel):
    ONLINE_MARKET = 'om'
    COMMISSION_SELLER = 'cs'
    REPRESENTATION_MARKET = 'rm'

    BUSINESS_TYPES = (
        (ONLINE_MARKET, 'فروشگاه اینترنتی '),
        (COMMISSION_SELLER, 'فروشنده پورسانتی'),
        (REPRESENTATION_MARKET, 'فروشگاه نمایندگی'),
    )

    name = models.CharField(max_length=150)
    domain_address = models.CharField(max_length=150, blank=True, null=True)
    logo = models.ImageField(upload_to=custom_upload_to, null=True, blank=True, default=None)
    api_token = models.CharField(max_length=150, blank=True, null=True, unique=True)
    primary_business_color = ColorField(default='#FF8700')
    secondary_business_color = ColorField(default='#002357')
    theme_business_color = ColorField(default='#dae3ed')
    business_owner_national_card_picture = models.ImageField(upload_to=custom_upload_to,
                                                             null=True, blank=True, default=None)
    about_us = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    business_type = models.CharField(max_length=2, choices=BUSINESS_TYPES, default=ONLINE_MARKET)
    admin = models.ForeignKey('users.User', on_delete=models.SET_NULL, related_name='business', blank=True, null=True)
    phone = models.CharField(max_length=11, blank=True, null=True)

    customers = models.ManyToManyField('users.User', related_name='businesses_customer')
    products = models.ManyToManyField('products.Product', related_name='businesses')

    @property
    def new_api_token(self):
        return binascii.hexlify(os.urandom(50)).decode()

    def save(self, *args, **kwargs):
        if not self.id:
            api_token = self.new_api_token
            while Business.objects.filter(api_token=api_token).exists():
                api_token = self.new_api_token
            self.api_token = api_token

        super().save(*args, **kwargs)

    class Meta(BaseModel.Meta):
        verbose_name = 'Business'
        permission_basename = 'business'
        permissions = (
            ('get.business', 'مشاهده کسب و کار'),
            ('create.business', 'تعریف کسب و کار'),
            ('update.business', 'ویرایش کسب و کار'),
            ('delete.business', 'حذف کسب و کار'),

            ('getOwn.business', 'مشاهده کسب و کار خود'),
            ('updateOwn.business', 'ویرایش کسب و کار خود'),
            ('deleteOwn.business', 'حذف کسب و کار خود'),
        )


class Store(BaseModel):
    CENTRAL = 'central'
    PACKING = 'packing'
    OTHER = 'other'

    STORE_TYPES = (
        (CENTRAL, 'انبار مرکزی '),
        (PACKING, 'واحد پردازش سفارشات'),
        (OTHER, 'انبار'),
    )

    code = models.CharField(max_length=10, choices=STORE_TYPES, default=OTHER)
    name = models.CharField(max_length=150)
    address = models.CharField(max_length=255, blank=True, null=True)
    storekeeper = models.ForeignKey('users.User', on_delete=models.SET_NULL, related_name='stores', blank=True, null=True)

    class Meta(BaseModel.Meta):
        verbose_name = 'Store'
        permission_basename = 'store'
        permissions = (
            ('get.store', 'مشاهده انبار'),
            ('create.store', 'تعریف انبار'),
            ('update.store', 'ویرایش انبار'),
            ('delete.store', 'حذف انبار'),

            ('getOwn.store', 'مشاهده انبار خود'),
            ('updateOwn.store', 'ویرایش انبار خود'),
            ('deleteOwn.store', 'حذف انبار خود'),
        )


class Currency(BaseModel):
    unique_code = models.IntegerField(unique=True, blank=True, null=True)
    name = models.CharField(max_length=150)
    exchange_rate_to_toman = DECIMAL(default=1)

    def exchange_to_toman(self, amount):
        if amount:
            return amount * self.exchange_rate_to_toman
        else:
            return 0

    def exchange_toman_to_currency(self, amount):
        if amount:
            return amount / self.exchange_rate_to_toman
        else:
            return 0

    class Meta(BaseModel.Meta):
        verbose_name = 'Currency'
        permission_basename = 'currency'
        permissions = (
            ('get.currency', 'مشاهده ارز'),
            ('create.currency', 'تعریف ارز'),
            ('update.currency', 'ویرایش ارز'),
            ('delete.currency', 'حذف ارز'),

            ('getOwn.currency', 'مشاهده ارز خود'),
            ('updateOwn.currency', 'ویرایش ارز خود'),
            ('deleteOwn.currency', 'حذف ارز خود'),
        )

    def __str__(self):
        return f'{self.name} >  {add_separator(self.exchange_rate_to_toman)} تومان '


class Supplier(BaseModel):
    name = models.CharField(max_length=150)
    bank_account_number = models.CharField(max_length=50, blank=True, null=True)
    bank_card_number = models.CharField(max_length=50, blank=True, null=True)
    bank_sheba_number = models.CharField(max_length=50, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=11, blank=True, null=True)
    admin = models.ForeignKey('users.User', on_delete=models.SET_NULL, related_name='supplies', blank=True, null=True)

    class Meta(BaseModel.Meta):
        verbose_name = 'Supplier'
        permission_basename = 'supplier'
        permissions = (
            ('get.supplier', 'مشاهده تامین کننده'),
            ('create.supplier', 'تعریف تامین کننده'),
            ('update.supplier', 'ویرایش تامین کننده'),
            ('delete.supplier', 'حذف تامین کننده'),

            ('getOwn.supplier', 'مشاهده تامین کننده خود'),
            ('updateOwn.supplier', 'ویرایش تامین کننده خود'),
            ('deleteOwn.supplier', 'حذف تامین کننده خود'),
        )
