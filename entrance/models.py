import datetime
from dateutil.relativedelta import relativedelta

from django.db import models

from helpers.models import BaseModel, DECIMAL, EXPLANATION
from main.models import Supplier, Currency, Store
from products.models import Product
from users.models import custom_upload_to, User


class EntrancePackage(BaseModel):
    manager = models.ForeignKey(User, related_name="entrance_packages",
                                on_delete=models.SET_NULL, blank=True, null=True)
    name = models.CharField(max_length=150)
    registration_date = models.DateField(blank=True, null=True)
    registration_time = models.TimeField(blank=True, null=True)
    supplier = models.ForeignKey(Supplier, related_name="entrance_packages",
                                 on_delete=models.SET_NULL, blank=True, null=True)
    store = models.ForeignKey(Store, related_name="entrance_packages",
                              on_delete=models.SET_NULL, blank=True, null=True)
    is_received = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    explanation = EXPLANATION()

    class Meta(BaseModel.Meta):
        verbose_name = 'EntrancePackage'
        permission_basename = 'entrance_packages'
        permissions = (
            ('get.entrance_packages', 'مشاهده پکیج ورودی'),
            ('create.entrance_packages', 'تعریف پکیج ورودی'),
            ('update.entrance_packages', 'ویرایش پکیج ورودی'),
            ('delete.entrance_packages', 'حذف پکیج ورودی'),

            ('getOwn.entrance_packages', 'مشاهده پکیج ورودی خود'),
            ('updateOwn.entrance_packages', 'ویرایش پکیج ورودی خود'),
            ('deleteOwn.entrance_packages', 'حذف پکیج ورودی خود'),
        )


class EntrancePackageItem(BaseModel):
    entrance_packages = models.ForeignKey(EntrancePackage, related_name="items",
                                          on_delete=models.SET_NULL, blank=True, null=True)
    product = models.ForeignKey(Product, related_name="entrance_package_items",
                                on_delete=models.SET_NULL, blank=True, null=True)
    product_code = models.CharField(max_length=150, null=True, blank=True)
    default_picture = models.ImageField(upload_to=custom_upload_to, null=True, blank=True, default=None)
    default_name = models.CharField(max_length=150)
    product_in_box_count = models.IntegerField(default=0)
    box_count = models.IntegerField(default=0)
    default_price = DECIMAL()
    currency = models.ForeignKey(Currency, related_name="entrance_package_items", on_delete=models.SET_NULL,
                                 blank=True, null=True)
    margin_profit_percent = DECIMAL()
    content_production_count = models.IntegerField(default=0)
    explanation = EXPLANATION()

    class Meta(BaseModel.Meta):
        verbose_name = 'EntrancePackageItem'
        permission_basename = 'entrance_package_item'
        permissions = (
            ('get.entrance_package_item', 'مشاهده ردیف پکیج ورودی'),
            ('create.entrance_package_item', 'تعریف ردیف پکیج ورودی'),
            ('update.entrance_package_item', 'ویرایش  ردیفپکیج ورودی'),
            ('delete.entrance_package_item', 'حذف ردیف پکیج ورودی'),

            ('getOwn.entrance_packages', 'مشاهده ردیف پکیج ورودی خود'),
            ('updateOwn.entrance_packages', 'ویرایش ردیف پکیج ورودی خود'),
            ('deleteOwn.entrance_packages', 'حذف ردیف پکیج ورودی خود'),
        )

    @property
    def product_count(self):
        return self.box_count * self.product_in_box_count


class StoreReceipt(BaseModel):
    storekeeper = models.ForeignKey(User, related_name="store_receipt", on_delete=models.SET_NULL,
                                    blank=True, null=True)
    entrance_packages = models.ForeignKey(EntrancePackage, related_name="store_receipt",
                                          on_delete=models.SET_NULL, blank=True, null=True)
    name = models.CharField(max_length=150)
    driver_name = models.CharField(max_length=255, blank=True, null=True)
    enter_date = models.DateField(blank=True, null=True)
    enter_time = models.TimeField(blank=True, null=True)
    store = models.ForeignKey(Store, related_name="store_receipt",
                              on_delete=models.SET_NULL, blank=True, null=True)
    box_count = models.IntegerField(default=0)

    explanation = EXPLANATION()

    class Meta(BaseModel.Meta):
        verbose_name = 'StoreReceipt'
        permission_basename = 'store_receipt'
        permissions = (
            ('get.store_receipt', 'مشاهده رسید ورود انبار'),
            ('create.store_receipt', 'تعریف رسید ورود انبار'),
            ('update.store_receipt', 'ویرایش رسید ورود انبار'),
            ('delete.store_receipt', 'حذف رسید ورود انبار'),

            ('getOwn.store_receipt', 'مشاهده رسید ورود انبار خود'),
            ('updateOwn.store_receipt', 'ویرایش رسید ورود انبار خود'),
            ('deleteOwn.store_receipt', 'حذف رسید ورود انبار خود'),
        )


class StoreReceiptItem(BaseModel):
    BOX = 'b'
    WITHOUT_BOX = 'w'

    TYPES = (
        (BOX, 'کارتون'),
        (WITHOUT_BOX, 'فله'),
    )
    type = models.CharField(max_length=1, choices=TYPES, default=BOX)

    store_receipt = models.ForeignKey(StoreReceipt, related_name="items", on_delete=models.SET_NULL,
                                      blank=True, null=True)
    product = models.ForeignKey(Product, related_name="store_receipt_items",
                                on_delete=models.SET_NULL, blank=True, null=True)
    product_in_box_count = models.IntegerField(default=0)
    box_count = models.IntegerField(default=0)

    product_code = models.CharField(max_length=150, null=True, blank=True)

    margin_profit_percent = DECIMAL()
    default_picture = models.ImageField(upload_to=custom_upload_to, null=True, blank=True, default=None)
    content_production_count = models.IntegerField(default=0)
    postal_weight = DECIMAL()
    length = models.IntegerField(blank=True, null=True)
    width = models.IntegerField(blank=True, null=True)
    height = models.IntegerField(blank=True, null=True)
    product_date = models.DateField(blank=True, null=True)
    expired_date = models.DateField(blank=True, null=True)
    new_product_shelf_code = models.IntegerField(null=True, blank=True)

    default_name = models.CharField(max_length=150)
    default_price = DECIMAL()
    currency = models.ForeignKey(Currency, related_name="store_receipt_items", on_delete=models.SET_NULL,
                                 blank=True, null=True)
    explanation = EXPLANATION()

    class Meta(BaseModel.Meta):
        verbose_name = 'StoreReceiptItem'
        permission_basename = 'store_receipt_item'
        permissions = (
            ('get.store_receipt', 'مشاهده ردیف رسید ورود انبار'),
            ('create.store_receipt', 'تعریف ردیف رسید ورود انبار'),
            ('update.store_receipt', 'ویرایش ردیف رسید ورود انبار'),
            ('delete.store_receipt', 'حذف ردیف رسید ورود انبار'),

            ('getOwn.store_receipt', 'مشاهده ردیف رسید ورود انبار خود'),
            ('updateOwn.store_receipt', 'ویرایش ردیف رسید ورود انبار خود'),
            ('deleteOwn.store_receipt', 'حذف ردیف رسید ورود انبار خود'),
        )

    @property
    def product_count(self):
        if self.type == self.BOX:
            return self.box_count * self.product_in_box_count
        else:
            return self.box_count