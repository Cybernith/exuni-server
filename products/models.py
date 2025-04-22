import datetime
import random
from decimal import Decimal

from dateutil.relativedelta import relativedelta
from django.core.exceptions import ValidationError

from django.db import models, transaction
from django.db.models import IntegerField, F, Sum, Q

from entrance.models import StoreReceiptItem
from helpers.functions import change_to_num
from helpers.models import BaseModel, DECIMAL, EXPLANATION
from main.models import Supplier, Currency, Business
from packing.models import OrderPackageItem
from shop.models import Rate, LimitedTimeOfferItems


def custom_upload_to(instance, filename):
    return 'images/{filename}'.format(filename=filename)


class Brand(BaseModel):
    name = models.CharField(max_length=150, unique=True)
    logo = models.ImageField(upload_to=custom_upload_to, null=True, blank=True, default=None)
    is_domestic = models.BooleanField(default=True)
    made_in = models.CharField(max_length=150, blank=True, null=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, related_name='brands', blank=True, null=True)

    class Meta(BaseModel.Meta):
        verbose_name = 'Brand'
        permission_basename = 'brand'
        permissions = (
            ('get.brand', 'مشاهده برند'),
            ('create.brand', 'تعریف برند'),
            ('update.brand', 'ویرایش برند'),
            ('delete.brand', 'حذف برند'),

            ('getOwn.brand', 'مشاهده برند خود'),
            ('updateOwn.brand', 'ویرایش برند خود'),
            ('deleteOwn.brand', 'حذف برند خود'),
        )


class Avail(BaseModel):
    name = models.CharField(max_length=150)
    explanation = models.CharField(max_length=255, blank=True, null=True)

    class Meta(BaseModel.Meta):
        verbose_name = 'Avail'
        permission_basename = 'avail'
        permissions = (
            ('get.avail', 'مشاهده فایده'),
            ('create.avail', 'تعریف فایده'),
            ('update.avail', 'ویرایش فایده'),
            ('delete.avail', 'حذف فایده'),

            ('getOwn.avail', 'مشاهده فایده خود'),
            ('updateOwn.avail', 'ویرایش فایده خود'),
            ('deleteOwn.avail', 'حذف فایده خود'),
        )


class ProductProperty(BaseModel):
    name = models.CharField(max_length=150)
    explanation = models.CharField(max_length=255, blank=True, null=True)

    class Meta(BaseModel.Meta):
        verbose_name = 'ProductProperty'
        permission_basename = 'product_property'
        permissions = (
            ('get.product_property', 'مشاهده خصوصیت کالا'),
            ('create.product_property', 'تعریف خصوصیت کالا'),
            ('update.product_property', 'ویرایش خصوصیت کالا'),
            ('delete.product_property', 'حذف خصوصیت کالا'),

            ('getOwn.product_property', 'مشاهده خصوصیت کالا خود'),
            ('updateOwn.product_property', 'ویرایش خصوصیت کالا خود'),
            ('deleteOwn.product_property', 'حذف خصوصیت کالا خود'),
        )


class Category(BaseModel):
    name = models.CharField(max_length=150)
    parent = models.ForeignKey('self', on_delete=models.PROTECT, related_name='children', blank=True, null=True)
    picture = models.ImageField(upload_to=custom_upload_to, null=True, blank=True, default=None)

    class Meta(BaseModel.Meta):
        verbose_name = 'Category'
        permission_basename = 'category'
        permissions = (
            ('get.category', 'مشاهده دسته بندی'),
            ('create.category', 'تعریف دسته بندی'),
            ('update.category', 'ویرایش دسته بندی'),
            ('delete.category', 'حذف دسته بندی'),

            ('getOwn.category', 'مشاهده دسته بندی خود'),
            ('updateOwn.category', 'ویرایش دسته بندی خود'),
            ('deleteOwn.category', 'حذف دسته بندی خود'),
        )


class Product(BaseModel):
    PUBLISHED = 'p'
    UNDER_REVIEW = 'u'

    STATUSES = (
        (PUBLISHED, 'منتشر شده'),
        (UNDER_REVIEW, 'در حال بررسی'),
    )

    product_id = models.CharField(max_length=150, unique=True,
                                  error_messages={'unique': "کالا با این شناسه از قبل در اکسونی ثبت شده"})

    sixteen_digit_code = models.CharField(max_length=16, blank=True, null=True)

    group_id = models.CharField(max_length=150, blank=True, null=True)

    name = models.CharField(max_length=150)

    picture = models.ImageField(upload_to=custom_upload_to, null=True, blank=True, default=None)
    first_texture_picture = models.ImageField(upload_to=custom_upload_to, null=True, blank=True, default=None)
    second_texture_picture = models.ImageField(upload_to=custom_upload_to, null=True, blank=True, default=None)

    first_inventory = models.IntegerField(default=0)
    shelf_code = models.CharField(max_length=20, null=True, blank=True)
    min_inventory = models.IntegerField(default=0)

    price = DECIMAL()
    sale_price = DECIMAL()
    shipping_cost = DECIMAL()
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, related_name='products', blank=True, null=True)
    profit_percent = DECIMAL()
    tax_percent = DECIMAL()

    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, related_name='products', blank=True, null=True)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, related_name='products', blank=True, null=True)

    explanation = models.TextField(blank=True, null=True)
    summary_explanation = models.TextField(blank=True, null=True)
    how_to_use = models.TextField(blank=True, null=True)

    product_date = models.DateField(blank=True, null=True)
    expired_date = models.DateField(blank=True, null=True)

    status = models.CharField(max_length=1, choices=STATUSES, default=UNDER_REVIEW)

    postal_weight = DECIMAL()
    length = models.IntegerField(blank=True, null=True)
    width = models.IntegerField(blank=True, null=True)
    height = models.IntegerField(blank=True, null=True)

    avails = models.ManyToManyField(Avail, related_name="products_with_this_avail", blank=True)
    properties = models.ManyToManyField(ProductProperty, related_name="products_with_this_properties", blank=True)

    category = models.ForeignKey(Category, related_name='products', on_delete=models.SET_NULL, blank=True, null=True)
    barcode = models.CharField(max_length=150, blank=True, null=True)

    @property
    def last_price(self):
        return self.price

    @property
    def rate(self):
        rate_count = Rate.objects.filter(product__id=self.id).count()
        return Rate.objects.filter(product__id=self.id).aggregate(Sum('level'))['level__sum'] / rate_count

    @property
    def type(self):
        return 'simple'

    @property
    def made_in(self):
        return self.brand.made_in

    @property
    def new_id(self):
        new_id = random.randint(1000000000, 9999999999)
        while Product.objects.filter(product_id=new_id).exists():
            new_id = random.randint(1000000000, 9999999999)
        return new_id

    @property
    def is_domestic(self):
        return self.brand.is_domestic

    @property
    def inventory(self):
        # return all inventory
        return self.first_inventory

    @property
    def is_freeze(self):
        return self.inventory <= self.min_inventory

    @property
    def is_expired_closed(self):
        if self.expired_date:
            return self.expired_date.__le__(datetime.date.today() - relativedelta(months=2))
        else:
            return False

    @property
    def content_production_completed(self):
        if self.picture and self.explanation and self.summary_explanation and self.postal_weight and self.width \
                and self.length and self.height:
            return True
        return False

    def change_price(self, new_price, user=None, note=''):
        current_price_object = getattr(self, 'current_price', None)
        old_price = current_price_object.price if current_price_object else 0
        if old_price != new_price:
            with transaction.atomic():
                if current_price_object:
                    current_price_object.price = new_price
                    current_price_object.save()
                else:
                    ProductPrice.objects.create(
                        product=self,
                        price=new_price
                    )
                ProductPriceHistory.objects.create(
                    product=self,
                    previous_price=old_price,
                    new_price=new_price,
                    changed_by=user,
                    note=note
                )

    @property
    def final_price(self):
        if hasattr(self, 'current_price'):
            return self.current_price.price
        raise ValueError(f"برای کالای {self.name} قیمت ثبت نشده")

    @property
    def effective_price(self):
        price = self.final_price
        now = datetime.datetime.now()
        offer = LimitedTimeOfferItems.objects.filter(
            Q(product=self) &
            Q(limited_time_offer__is_active=True) &
            Q(limited_time_offer__from_date_time__gte=now) &
            Q(limited_time_offer__to_date_time__lte=now)
        ).first()
        if offer:
            effective_price = price - offer.offer_amount
            return effective_price if effective_price > 0 else Decimal('0.00')
        return price

    class Meta(BaseModel.Meta):
        verbose_name = 'Product'
        permission_basename = 'product'
        permissions = (
            ('get.product', 'مشاهده محصول'),
            ('create.product', 'تعریف محصول'),
            ('update.product', 'ویرایش محصول'),
            ('delete.product', 'حذف محصول'),

            ('getOwn.product', 'مشاهده محصول خود'),
            ('updateOwn.product', 'ویرایش محصول خود'),
            ('deleteOwn.product', 'حذف محصول خود'),
        )

    def save(self, *args, **kwargs):
        if not self.product_id:
            self.product_id = self.new_id
        super().save(*args, **kwargs)


class ProductGallery(BaseModel):
    product = models.ForeignKey(Product, related_name='gallery', on_delete=models.CASCADE)
    picture = models.ImageField(upload_to=custom_upload_to, null=True, blank=True, default=None)

    class Meta(BaseModel.Meta):
        verbose_name = 'ProductGallery'
        permission_basename = 'product_gallery'
        permissions = (
            ('get.product_gallery', 'مشاهده گالری محصول'),
            ('create.product_gallery', 'تعریف گالری محصول'),
            ('update.product_gallery', 'ویرایش گالری محصول'),
            ('delete.product_gallery', 'حذف گالری محصول'),

            ('getOwn.product_gallery', 'مشاهده گالری محصول خود'),
            ('updateOwn.product_gallery', 'ویرایش گالری محصول خود'),
            ('deleteOwn.product_gallery', 'حذف گالری محصول خود'),
        )


class ProductInventory(models.Model):
    product = models.OneToOneField(Product, related_name='inventory', on_delete=models.CASCADE)
    inventory = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    def add_to_inventory(self, val):
        self.inventory += val
        self.save()

    def reduce_inventory(self, val, user=None):
        with transaction.atomic():
            if self.inventory < val:
                raise ValidationError('موجودی کالا کافی نیست')
            previous_quantity = self.inventory
            self.inventory -= val
            self.save()

            ProductInventoryHistory.objects.create(
                inventory=self,
                action=ProductInventoryHistory.DECREASE,
                amount=val,
                previous_quantity=previous_quantity,
                new_quantity=self.inventory,
                changed_by=user
            )

    def increase_inventory(self, val, user=None):
        with transaction.atomic():
            previous_quantity = self.inventory
            self.inventory += val
            self.save()

            ProductInventoryHistory.objects.create(
                inventory=self,
                action=ProductInventoryHistory.INCREASE,
                amount=val,
                previous_quantity=previous_quantity,
                new_quantity=self.inventory,
                changed_by=user
            )

    def __str__(self):
        return '{} - {}'.format(self.product.name, self.inventory)

    #def set_product_inventory(self):
    #    self.inventory = self.product.first_inventory
    #
    #    entrance_items = StoreReceiptItem.objects.filter(product=self.product).annotate(
    #        product_count=Sum((F('number_of_box') * F('number_of_products_per_box')), output_field=IntegerField()),
    #    ).aggregate(
    #        Sum('product_count'),
    #    )
    #
    #    sale_items = OrderPackageItem.objects.filter(product=self.product).aggregate(
    #        Sum('quantity'),
    #    )
    #
    #    self.inventory += change_to_num(entrance_items['product_count__sum'])
    #    self.inventory -= change_to_num(sale_items['quantity__sum'])
    #    self.save()


class ProductInventoryHistory(models.Model):
    INCREASE = 'i'
    DECREASE = 'd'

    ACTION_CHOICES = (
        (INCREASE, 'افزایش'),
        (DECREASE, 'کاهش'),
    )

    inventory = models.ForeignKey(ProductInventory, related_name='history', on_delete=models.CASCADE)
    action = models.CharField(max_length=1, choices=ACTION_CHOICES)
    amount = models.IntegerField()
    previous_quantity = models.IntegerField()
    new_quantity = models.IntegerField()
    timestamp = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return f"{self.get_action_display()} موجودی {self.inventory.product.name} "


class ProductPrice(models.Model):
    product = models.OneToOneField(Product, related_name='current_price', on_delete=models.CASCADE)
    price = DECIMAL()
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} - {}'.format(self.product.name, self.price)


class ProductPriceHistory(models.Model):
    product = models.OneToOneField(Product, related_name='price_history', on_delete=models.CASCADE)
    previous_price = DECIMAL()
    new_price = DECIMAL()
    changed_at = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, blank=True, null=True)
    note = EXPLANATION()

    class Meta:
        ordering = ['-changed_at']

    def __str__(self):
        return f"تغییر قیمت {self.product.name} از {self.previous_price} به {self.new_price}"


