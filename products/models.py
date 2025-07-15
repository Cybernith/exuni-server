import datetime
import random
from decimal import Decimal

from dateutil.relativedelta import relativedelta
from django.core.exceptions import ValidationError

from django.db import models, transaction
from django.db.models import IntegerField, F, Sum, Q, Avg

from crm.services.inventory_reminder import notify_users_if_in_stock
from entrance.models import StoreReceiptItem
from helpers.functions import change_to_num
from helpers.models import BaseModel, DECIMAL, EXPLANATION
from main.models import Supplier, Currency, Business
from packing.models import OrderPackageItem
from products.managers import ProductManager
from shop.models import Rate, LimitedTimeOfferItems


def custom_upload_to(instance, filename):
    return 'images/{filename}'.format(filename=filename)


class Brand(BaseModel):
    unique_code = models.IntegerField(unique=True, null=True)
    slug = models.CharField(max_length=150, blank=True, null=True)
    name = models.CharField(max_length=150, unique=True)
    logo = models.ImageField(upload_to=custom_upload_to, null=True, blank=True, default=None)
    is_domestic = models.BooleanField(default=True)
    made_in = models.CharField(max_length=150, blank=True, null=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, related_name='brands', blank=True, null=True)

    class Meta(BaseModel.Meta):
        verbose_name_plural = 'برند'
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

    def __str__(self):
        return self.name


class Avail(BaseModel):
    name = models.CharField(max_length=255)
    explanation = models.TextField(blank=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='children', blank=True, null=True)
    image = models.ImageField(upload_to=custom_upload_to, null=True, blank=True, default=None)

    class Meta(BaseModel.Meta):
        verbose_name_plural = 'خواص محصولات'
        permission_basename = 'avail'
        permissions = (
            ('get.avail', 'مشاهده خواص'),
            ('create.avail', 'تعریف خواص'),
            ('update.avail', 'ویرایش خواص'),
            ('delete.avail', 'حذف خواص'),

            ('getOwn.avail', 'مشاهده خواص خود'),
            ('updateOwn.avail', 'ویرایش خواص خود'),
            ('deleteOwn.avail', 'حذف خواص خود'),
        )

    def get_all_descendants(self):
        descendants = []
        children = Category.objects.filter(parent=self)
        for child in children:
            descendants.append(child)
            descendants.extend(child.get_all_descendants())
        return descendants

    def __str__(self):
        names = [self.name]
        parent = self.parent
        while parent:
            names.append(parent.name)
            parent = parent.parent
        return " > ".join(reversed(names))


class Categorization(BaseModel):
    name = models.CharField(max_length=255)
    explanation = models.TextField(blank=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='children', blank=True, null=True)
    image = models.ImageField(upload_to=custom_upload_to, null=True, blank=True, default=None)

    class Meta(BaseModel.Meta):
        verbose_name_plural = 'دسته بندی محصولات '
        permission_basename = 'categorization'
        permissions = (
            ('get.categorization', 'مشاهده دسته بندی محصولات '),
            ('create.categorization', 'تعریف دسته بندی محصولات '),
            ('update.categorization', 'ویرایش دسته بندی محصولات '),
            ('delete.categorization', 'حذف دسته بندی محصولات '),

            ('getOwn.categorization', 'مشاهده دسته بندی محصولات  خود'),
            ('updateOwn.categorization', 'ویرایش دسته بندی محصولات  خود'),
            ('deleteOwn.categorization', 'حذف دسته بندی محصولات  خود'),
        )

    def get_all_descendants(self):
        descendants = []
        children = Category.objects.filter(parent=self)
        for child in children:
            descendants.append(child)
            descendants.extend(child.get_all_descendants())
        return descendants

    def __str__(self):
        names = [self.name]
        parent = self.parent
        while parent:
            names.append(parent.name)
            parent = parent.parent
        return " > ".join(reversed(names))


class Feature(BaseModel):
    name = models.CharField(max_length=255)
    explanation = models.TextField(blank=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='children', blank=True, null=True)
    image = models.ImageField(upload_to=custom_upload_to, null=True, blank=True, default=None)

    class Meta(BaseModel.Meta):
        verbose_name_plural = 'ویژگی محصولات'
        permission_basename = 'avail'
        permissions = (
            ('get.avail', 'مشاهده ویژگی محصولات '),
            ('create.avail', 'تعریف ویژگی محصولات '),
            ('update.avail', 'ویرایش ویژگی محصولات '),
            ('delete.avail', 'حذف ویژگی محصولات '),

            ('getOwn.avail', 'مشاهده ویژگی محصولات  خود'),
            ('updateOwn.avail', 'ویرایش ویژگی محصولات  خود'),
            ('deleteOwn.avail', 'حذف ویژگی محصولات  خود'),
        )

    def get_all_descendants(self):
        descendants = []
        children = Category.objects.filter(parent=self)
        for child in children:
            descendants.append(child)
            descendants.extend(child.get_all_descendants())
        return descendants

    def __str__(self):
        names = [self.name]
        parent = self.parent
        while parent:
            names.append(parent.name)
            parent = parent.parent
        return " > ".join(reversed(names))


class ProductProperty(BaseModel):
    unique_code = models.IntegerField(unique=True, null=True)
    name = models.CharField(max_length=150)
    slug = models.CharField(max_length=150, blank=True, null=True)
    explanation = models.CharField(max_length=255, blank=True, null=True)

    class Meta(BaseModel.Meta):
        verbose_name_plural = 'خصوصیت کالا'
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

    def __str__(self):
        return self.name


class ProductPropertyTerm(BaseModel):
    product_property = models.ForeignKey(ProductProperty, related_name='terms',
                                         on_delete=models.CASCADE, blank=True, null=True)
    unique_code = models.IntegerField(unique=True, null=True)
    name = models.CharField(max_length=150, blank=True, null=True)
    slug = models.CharField(max_length=150, blank=True, null=True)
    explanation = models.CharField(max_length=255, blank=True, null=True)

    class Meta(BaseModel.Meta):
        verbose_name_plural = 'آیتم خصوصیت کالا'
        permission_basename = 'product_property_term'
        permissions = (
            ('get.product_property_term', 'مشاهده آیتم خصوصیت کالا'),
            ('create.product_property_term', 'تعریف آیتم خصوصیت کالا'),
            ('update.product_property_term', 'ویرایش آیتم خصوصیت کالا'),
            ('delete.product_property_term', 'حذف آیتم خصوصیت کالا'),

            ('getOwn.product_property_term', 'مشاهده آیتم خصوصیت کالا خود'),
            ('updateOwn.product_property_term', 'ویرایش آیتم خصوصیت کالا خود'),
            ('deleteOwn.product_property_term', 'حذف آیتم خصوصیت کالا خود'),
        )

    def __str__(self):
        return self.product_property.name + ' >  ' + self.name


class Category(BaseModel):
    slug = models.SlugField(max_length=255)
    unique_code = models.IntegerField(unique=True)
    parent_unique_code = models.IntegerField(blank=True, null=True)
    name = models.CharField(max_length=255)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='children', blank=True, null=True)
    picture = models.ImageField(upload_to=custom_upload_to, null=True, blank=True, default=None)

    class Meta(BaseModel.Meta):
        verbose_name_plural = 'دسته بندی'
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

    def get_all_descendants(self):
        descendants = []
        children = Category.objects.filter(parent=self)
        for child in children:
            descendants.append(child)
            descendants.extend(child.get_all_descendants())  # Recursive call to fetch all nested children
        return descendants

    def __str__(self):
        names = [self.name]
        parent = self.parent
        while parent:
            names.append(parent.name)
            parent = parent.parent
        return " > ".join(reversed(names))


class Product(BaseModel):
    PENDING = 'pending'
    DRAFT = 'draft'
    PUBLISHED = 'publish'

    STATUSES = (
        (PENDING, 'در انتظار'),
        (DRAFT, 'پیش‌نویس'),
        (PUBLISHED, 'منتشر شده'),

    )

    SIMPLE = 'simple'
    VARIABLE = 'variable'
    VARIATION = 'variation'

    TYPES = (
        (SIMPLE, 'بدون متغیر'),
        (VARIABLE, 'دارای متغیر'),
        (VARIATION, 'متغیر'),
    )

    PERCENT = 'percent'
    AMOUNT = 'amount'

    PROFIT_TYPES = (
        (PERCENT, ' درصدی'),
        (AMOUNT, ' مبلغی'),
    )
    status = models.CharField(max_length=7, choices=STATUSES, default=PENDING)
    product_type = models.CharField(max_length=9, choices=TYPES, default=SIMPLE)
    variation_of = models.ForeignKey('self', on_delete=models.CASCADE, related_name='variations', blank=True, null=True)
    variation_title = models.CharField(max_length=150, blank=True, null=True)

    product_id = models.CharField(max_length=255, blank=True, null=True)
    slug = models.SlugField(max_length=255, blank=True, null=True)

    sixteen_digit_code = models.CharField(max_length=50, blank=True, null=True)

    group_id = models.CharField(max_length=150, blank=True, null=True)

    name = models.CharField(max_length=150)

    feature_vector = models.BinaryField(null=True, blank=True)
    picture = models.ImageField(upload_to=custom_upload_to, null=True, blank=True, default=None)
    first_texture_picture = models.ImageField(upload_to=custom_upload_to, null=True, blank=True, default=None)
    second_texture_picture = models.ImageField(upload_to=custom_upload_to, null=True, blank=True, default=None)

    first_inventory = models.IntegerField(default=0, null=True, blank=True)
    shelf_code = models.CharField(max_length=20, null=True, blank=True)
    min_inventory = models.IntegerField(default=0)

    price = DECIMAL(null=True, blank=True)
    sale_price = DECIMAL(null=True, blank=True)
    regular_price = DECIMAL(null=True, blank=True)
    currency_price = DECIMAL(null=True, blank=True)

    shipping_cost = DECIMAL()
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, related_name='products', blank=True, null=True)

    profit_type = models.CharField(choices=PROFIT_TYPES, default=PERCENT, max_length=10)
    profit_margin = DECIMAL(null=True, blank=True)

    discount_type = models.CharField(choices=PROFIT_TYPES, default=PERCENT, max_length=10)
    discount_margin = DECIMAL(default=0)

    base_price = DECIMAL(null=True, blank=True)
    profit_amount = DECIMAL(null=True, blank=True)
    discount_amount = DECIMAL(null=True, blank=True)

    taxable = models.BooleanField(default=True)
    tax_percent = DECIMAL()

    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, related_name='products', blank=True, null=True)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, related_name='products', blank=True, null=True)

    explanation = models.TextField(blank=True, null=True)
    summary_explanation = models.TextField(blank=True, null=True)
    how_to_use = models.TextField(blank=True, null=True)

    product_date = models.DateField(blank=True, null=True)
    expired_date = models.DateField(blank=True, null=True)

    postal_weight = DECIMAL()
    length = models.IntegerField(blank=True, null=True)
    width = models.IntegerField(blank=True, null=True)
    height = models.IntegerField(blank=True, null=True)

    avails = models.ManyToManyField(Avail, related_name="products_with_this_avail", blank=True)
    properties = models.ManyToManyField(ProductProperty, related_name="products_with_this_properties", blank=True)

    category = models.ManyToManyField(Category, related_name='products', blank=True, null=True)
    barcode = models.CharField(max_length=150, blank=True, null=True)

    objects = ProductManager()


    def set_legend_pricing(self):
        if not self.profit_margin:
            raise ValidationError('مقدار حاشیه سود موجود نیست')
        if not self.base_price:
            raise ValidationError('قیمت پایه موجود نیست')

        if self.profit_type == self.PERCENT:
            profit_amount = self.base_price / Decimal(100) * self.profit_margin
        else:
            profit_amount = self.profit_margin

        price_with_profit = profit_amount + self.base_price

        if self.discount_type == self.PERCENT:
            discount_amount = price_with_profit / Decimal(100) * self.discount_margin
        else:
            discount_amount = self.discount_margin

        final_amount = price_with_profit - discount_amount

        self.regular_price = price_with_profit
        self.price = final_amount
        self.profit_amount = profit_amount
        self.discount_amount = discount_amount
        self.save()


    @property
    def confirmed_comments(self):
        return self.product_comments.filter(reply__isnull=True, confirmed=True)

    @property
    def last_price(self):
        return self.price

    @property
    def rate(self):
        return self.products_rates.aggregate(rate=Avg('level'))['rate'] or 0

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
        return self.current_inventory.inventory <= self.min_inventory

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
    def in_wish_list_count(self):
        return self.products_in_wish_list.count()

    def comments_count(self):
        return self.product_comments.filter(confirmed=True).count()

    @property
    def calculate_current_inventory(self):
        if hasattr(self, 'current_inventory'):
            return self.current_inventory.inventory
        raise ValueError(f"برای کالای {self.name} موجودی ثبت نشده")

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

    @property
    def has_offer(self):
        now = datetime.datetime.now()
        return LimitedTimeOfferItems.objects.filter(
            Q(product=self) &
            Q(limited_time_offer__is_active=True) &
            Q(limited_time_offer__from_date_time__gte=now) &
            Q(limited_time_offer__to_date_time__lte=now)
        ).exists()

    @property
    def offer_amount(self):
        now = datetime.datetime.now()
        offer = LimitedTimeOfferItems.objects.filter(
            Q(product=self) &
            Q(limited_time_offer__is_active=True) &
            Q(limited_time_offer__from_date_time__gte=now) &
            Q(limited_time_offer__to_date_time__lte=now)
        ).first()
        if offer:
            return offer.offer_amount
        return 0

    @property
    def offer_display(self):
        now = datetime.datetime.now()
        offer = LimitedTimeOfferItems.objects.filter(
            Q(product=self) &
            Q(limited_time_offer__is_active=True) &
            Q(limited_time_offer__from_date_time__gte=now) &
            Q(limited_time_offer__to_date_time__lte=now)
        ).first()
        if offer:
            return offer.offer_display
        return None

    def set_first_inventory(self):
        inventory = ProductInventory.objects.create(product=self, inventory=0)
        if self.first_inventory:
            if self.first_inventory < 0:
                self.first_inventory = 0
            inventory.increase_inventory(val=self.first_inventory, first_inventory=True)

    def set_first_price(self):
        price = ProductPrice.objects.create(product=self, price=0)
        if self.price:
            price.increase_price(val=self.price)

    class Meta(BaseModel.Meta):
        verbose_name_plural = 'محصول'
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

    def __str__(self):
        if self.product_type == self.SIMPLE:
            return "نام {} کد {}".format(
                self.name, self.sixteen_digit_code
            )
        elif self.product_type == self.VARIABLE:
            return "نام {} دارای متغیر".format(
                self.name
            )
        else:
            return "نام   {} {} کد {}"


    def save(self, *args, **kwargs):
        first_register = not self.id
        if first_register:
            self.product_id = self.new_id
        # if not self.product_id:
        #     self.product_id = self.new_id
        super().save(*args, **kwargs)
        if first_register:
            self.set_first_inventory()
            self.set_first_price()


class ProductAttribute(BaseModel):
    product = models.ForeignKey(Product, related_name='attributes', on_delete=models.CASCADE)
    product_property = models.ForeignKey(ProductProperty, related_name='property_attributes', on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    explanation = models.CharField(max_length=255, blank=True, null=True)

    class Meta(BaseModel.Meta):
        verbose_name_plural = 'صفت  کالا'
        permission_basename = 'product_attribute'
        permissions = (
            ('get.product_attribute', 'مشاهده صفت  کالا'),
            ('create.product_attribute', 'تعریف صفت  کالا'),
            ('update.product_attribute', 'ویرایش صفت  کالا'),
            ('delete.product_attribute', 'حذف صفت  کالا'),

            ('getOwn.product_attribute', 'مشاهده صفت  کالا خود'),
            ('updateOwn.product_attribute', 'ویرایش صفت  کالا خود'),
            ('deleteOwn.product_attribute', 'حذف صفت  کالا خود'),
        )

    def __str__(self):
        return "محصول {} > {}".format(
            self.product.name, self.product_property.name
        )


class ProductAttributeTerm(BaseModel):
    product_attribute = models.ForeignKey(ProductAttribute, related_name='terms', on_delete=models.CASCADE)
    terms = models.ManyToManyField(ProductPropertyTerm, related_name='attribute_in_products')

    class Meta(BaseModel.Meta):
        verbose_name_plural = 'آیتم صفت  کالا'
        permission_basename = 'product_attribute_term'
        permissions = (
            ('get.product_attribute_term', 'مشاهده آیتم صفت  کالا'),
            ('create.product_attribute_term', 'تعریف آیتم صفت  کالا'),
            ('update.product_attribute_term', 'ویرایش آیتم صفت  کالا'),
            ('delete.product_attribute_term', 'حذف آیتم صفت  کالا'),

            ('getOwn.product_attribute_term', 'مشاهده آیتم صفت  کالا خود'),
            ('updateOwn.product_attribute_term', 'ویرایش آیتم صفت  کالا خود'),
            ('deleteOwn.product_attribute_term', 'حذف آیتم صفت  کالا خود'),
        )

    def __str__(self):
        terms = ''
        for term in self.terms.all():
            terms += term.name
            terms += ' | '
        return "محصول {} > {} > {}".format(
            self.product_attribute.product.name, self.product_attribute.product_property.name, terms
        )


class ProductGallery(BaseModel):
    product = models.ForeignKey(Product, related_name='gallery', on_delete=models.CASCADE)
    picture = models.ImageField(upload_to=custom_upload_to, null=True, blank=True, default=None)

    class Meta(BaseModel.Meta):
        verbose_name_plural = 'گالری محصول'
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
    def __str__(self):
        return self.product.name + ' تصویر '


class ProductInventory(models.Model):
    product = models.OneToOneField(Product, related_name='current_inventory', on_delete=models.CASCADE)
    inventory = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    def add_to_inventory(self, val):
        self.inventory += val
        self.save()

    def reduce_inventory(self, val, user=None):
        if not val > 0:
            raise ValidationError('reduce value most be positive number')

        with transaction.atomic():
            if self.inventory < val:
                raise ValidationError(f"موجودی محصول {self.product.name} کافی نیست.")
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

    def increase_inventory(self, val, user=None, first_inventory=False):
        if not val >= 0:
            raise ValidationError('increase value most be positive number')
        else:
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
                    first_inventory=first_inventory,
                    changed_by=user
                )

                if previous_quantity <= 0 < self.inventory:
                    notify_users_if_in_stock(self.product)


    def __str__(self):
        return '{} موجودی {}'.format(self.product.name, self.inventory)

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
    first_inventory = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.get_action_display()} موجودی {self.inventory.product.name} "


class ProductPrice(models.Model):
    product = models.OneToOneField(Product, related_name='current_price', on_delete=models.CASCADE)
    price = DECIMAL()
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} قیمت {}'.format(self.product.name, self.price)

    def reduce_price(self, val, user=None, note=''):
        with transaction.atomic():
            now = datetime.datetime.now()
            previous_price = self.price
            new_price = previous_price - val
            self.last_updated = now
            self.price = new_price
            self.save()

            ProductPriceHistory.objects.create(
                product=self.product,
                action=ProductPriceHistory.DECREASE,
                previous_price=previous_price,
                new_price=new_price,
                changed_by=user,
                changed_at=now,
                note=note
            )

    def increase_price(self, val, user=None, note=''):
        with transaction.atomic():
            now = datetime.datetime.now()
            previous_price = self.price
            new_price = previous_price + val
            self.last_updated = now
            self.price = new_price
            self.save()

            ProductPriceHistory.objects.create(
                product=self.product,
                action=ProductPriceHistory.INCREASE,
                previous_price=previous_price,
                new_price=new_price,
                changed_by=user,
                changed_at=now,
                note=note
            )


class ProductPriceHistory(models.Model):
    INCREASE = 'i'
    DECREASE = 'd'

    ACTION_CHOICES = (
        (INCREASE, 'افزایش'),
        (DECREASE, 'کاهش'),
    )
    product = models.OneToOneField(Product, related_name='price_history', on_delete=models.CASCADE)
    action = models.CharField(max_length=1, choices=ACTION_CHOICES, default=INCREASE)
    previous_price = DECIMAL()
    new_price = DECIMAL()
    changed_at = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, blank=True, null=True)
    note = EXPLANATION()

    class Meta:
        ordering = ['-changed_at']

    def __str__(self):
        return f"تغییر قیمت {self.product.name} از {self.previous_price} به {self.new_price}"


