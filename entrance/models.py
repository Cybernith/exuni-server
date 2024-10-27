import datetime
from dateutil.relativedelta import relativedelta

from django.db import models

from helpers.models import BaseModel, DECIMAL, EXPLANATION
from main.models import Supplier, Currency, Store
from products.models import Product
from users.models import custom_upload_to, User

def excel_upload_to(instance, filename):
    return 'files/{filename}'.format(filename=filename)


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
    currency = models.ForeignKey(Currency, related_name="entrance_packages",
                              on_delete=models.PROTECT, blank=True, null=True)
    is_received = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    explanation = EXPLANATION()
    entrance_file = models.FileField(upload_to=excel_upload_to, blank=True, null=True)

    is_inserted = models.BooleanField(default=False)

    class Meta(BaseModel.Meta):
        verbose_name = 'EntrancePackage'
        permission_basename = 'entrance_package'
        permissions = (
            ('get.entrance_package', 'مشاهده پکیج ورودی'),
            ('create.entrance_package', 'تعریف پکیج ورودی'),
            ('update.entrance_package', 'ویرایش پکیج ورودی'),
            ('delete.entrance_package', 'حذف پکیج ورودی'),

            ('getOwn.entrance_package', 'مشاهده پکیج ورودی خود'),
            ('updateOwn.entrance_package', 'ویرایش پکیج ورودی خود'),
            ('deleteOwn.entrance_package', 'حذف پکیج ورودی خود'),
        )

    @property
    def remain_items(self):
        items = {}
        for row in self.items.all():
            items[row.default_name] = {
                'number_of_products_per_box': row.number_of_products_per_box,
                'number_of_box': row.number_of_box,
            }

        for row in StoreReceiptItem.objects.filter(store_receipt__entrance_packages=self):
            items[row.default_name]['number_of_box'] -= row.number_of_box

        return items

    @property
    def inserted_to_store(self):
        remain = self.remain_items
        for key in remain:
            if remain[key]['number_of_box'] > 0:
                return False
        return True


class EntrancePackageItem(BaseModel):
    MANUAL = 'm'
    WITH_AMOUNT = 'a'
    WITH_PERCENTAGE = 'p'

    IN_CASE_OF_SALES_TYPES = (
        (WITH_AMOUNT, 'مبلغ'),
        (WITH_PERCENTAGE, 'درصد'),
    )

    entrance_package = models.ForeignKey(EntrancePackage, related_name="items",
                                          on_delete=models.SET_NULL, blank=True, null=True)
    product = models.ForeignKey(Product, related_name="entrance_package_items",
                                on_delete=models.SET_NULL, blank=True, null=True)
    product_code = models.CharField(max_length=150, null=True, blank=True)
    default_picture = models.ImageField(upload_to=custom_upload_to, null=True, blank=True, default=None)
    default_name = models.CharField(max_length=150)
    number_of_products_per_box = models.IntegerField(default=0)
    number_of_products = models.IntegerField(default=0)
    number_of_box = models.IntegerField(default=1)
    sixteen_digit_code = models.CharField(max_length=16, blank=True, null=True)
    barcode = models.CharField(max_length=100, blank=True, null=True)
    default_price = DECIMAL()
    price_in_case_of_sale = DECIMAL(default=0)
    in_case_of_sale_type = models.CharField(max_length=2, choices=IN_CASE_OF_SALES_TYPES, default=WITH_AMOUNT)
    currency = models.ForeignKey(Currency, related_name="entrance_package_items", on_delete=models.SET_NULL,
                                 blank=True, null=True)
    discount = DECIMAL(default=0)
    discount_type = models.CharField(max_length=2, choices=IN_CASE_OF_SALES_TYPES, default=WITH_AMOUNT)

    margin_profit_percent = DECIMAL()
    price_sum = DECIMAL()
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
    def in_case_of_sale(self):
        if self.in_case_of_sale_type == self.WITH_AMOUNT:
            return self.net_purchase_price + self.price_in_case_of_sale
        else:
            return self.net_purchase_price + (self.net_purchase_price * self.price_in_case_of_sale / 100)

    @property
    def final_price_after_discount(self):
        if self.discount_type == self.WITH_AMOUNT:
            return self.in_case_of_sale - self.discount
        else:
            return self.in_case_of_sale + (self.in_case_of_sale * self.discount / 100)

    @property
    def product_count(self):
        return self.number_of_box * self.number_of_products_per_box

    @property
    def net_purchase_price(self):
        if self.default_price:
            return self.default_price
        elif self.price_sum and self.number_of_products:
            return round(self.price_sum / self.number_of_products)
        else:
            return 0

    def save(self, *args, **kwargs):
        if not self.number_of_products and self.number_of_products_per_box and self.number_of_box:
            self.number_of_products = self.number_of_products_per_box * self.number_of_box

        if self.entrance_package.items.filter(default_name=self.default_name).exists():
            for item in self.entrance_package.items.filter(default_name=self.default_name):
                self.number_of_products += item.number_of_products
                self.price_sum += item.price_sum
                item.delete()

        if not self.price_sum:
            if self.number_of_products_per_box and self.number_of_box:
                self.price_sum = self.number_of_products_per_box * self.number_of_box

        super().save(*args, **kwargs)


class EntrancePackageFileColumn(BaseModel):
    PRODUCT_CODE = 'pc'
    PRODUCT_NAME = 'pn'
    PRODUCT_PRICE = 'pp'
    NUMBER_OF_BOXES = 'nb'
    NUMBER_OF_PRODUCTS_PER_BOX = 'pb'
    NUMBER_OF_PRODUCTS = 'np'
    SIXTEEN_DIGIT_CODE = 'sd'
    PRICE_IN_CASE_OF_SALE = 'ic'
    BARCODE = 'ba'
    IMAGE = 'im'
    PRICE_SUM = 'ps'

    KEYS = (
        (PRODUCT_PRICE, 'مبلغ محصول'),
        (PRODUCT_NAME, 'نام محصول'),
        (PRODUCT_CODE, 'کد محصول'),
        (NUMBER_OF_BOXES, 'تعداد کارتون'),
        (NUMBER_OF_PRODUCTS_PER_BOX, 'تعداد محصول در کارتون'),
        (NUMBER_OF_PRODUCTS, 'تعداد محصول'),
        (SIXTEEN_DIGIT_CODE, 'کد 16 رقمی'),
        (PRICE_IN_CASE_OF_SALE, 'قیمت در صورت فروش'),
        (BARCODE, 'بارکد'),
        (IMAGE, 'تصویر'),
        (PRICE_SUM, 'مبلغ کل'),
    )

    entrance_package = models.ForeignKey(EntrancePackage, related_name="file_columns", on_delete=models.CASCADE)
    key = models.CharField(max_length=2, choices=KEYS)
    column_number = models.IntegerField()
    in_case_of_sale_type = models.CharField(max_length=2, choices=EntrancePackageItem.IN_CASE_OF_SALES_TYPES, blank=True, null=True)


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
    is_verified = models.BooleanField(default=False)

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
    number_of_products_per_box = models.IntegerField(default=0)
    number_of_box = models.IntegerField(default=1)

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
            return self.number_of_box * self.number_of_products_per_box
        else:
            return self.number_of_products_per_box
