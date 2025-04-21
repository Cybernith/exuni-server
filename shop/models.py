import datetime

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q, Sum, F, DecimalField

from helpers.functions import datetime_to_str, add_separator
from helpers.models import BaseModel, DECIMAL
import random


class Cart(BaseModel):
    customer = models.ForeignKey('users.User', related_name='cart_items', on_delete=models.PROTECT)
    product = models.ForeignKey('products.Product', related_name='products_in_cart',  on_delete=models.PROTECT)
    quantity = models.IntegerField(default=1)

    class Meta(BaseModel.Meta):
        verbose_name = 'Cart'
        permission_basename = 'cart'
        permissions = (
            ('get.cart', 'مشاهده آیتم سبد خرید'),
            ('create.cart', 'تعریف آیتم سبد خرید'),
            ('update.cart', 'ویرایش آیتم سبد خرید'),
            ('delete.cart', 'حذف آیتم سبد خرید'),

            ('getOwn.cart', 'مشاهده آیتم سبد خرید خود'),
            ('updateOwn.cart', 'ویرایش آیتم سبد خرید خود'),
            ('deleteOwn.cart', 'حذف آیتم سبد خرید خود'),
        )

    def __str__(self):
        return "محصول {} در سبد {}".format(self.product.name, self.customer.name)


class WishList(BaseModel):
    customer = models.ForeignKey('users.User', related_name='wish_list_items', on_delete=models.CASCADE)
    product = models.ForeignKey('products.Product', related_name='products_in_wish_list',  on_delete=models.CASCADE)

    class Meta(BaseModel.Meta):
        verbose_name = 'WishList'
        permission_basename = 'wish_list'
        permissions = (
            ('get.wish_list', 'مشاهده آیتم علاقه مندی ها'),
            ('create.wish_list', 'تعریف آیتم علاقه مندی ها'),
            ('update.wish_list', 'ویرایش آیتم علاقه مندی ها'),
            ('delete.wish_list', 'حذف آیتم علاقه مندی ها'),

            ('getOwn.wish_list', 'مشاهده آیتم علاقه مندی های خود'),
            ('updateOwn.wish_list', 'ویرایش آیتم علاقه مندی های خود'),
            ('deleteOwn.wish_list', 'حذف آیتم علاقه مندی های خود'),
        )

    def __str__(self):
        return "محصول {} در علاقه مندی های {}".format(self.product.name, self.customer.name)


class Comparison(BaseModel):
    customer = models.ForeignKey('users.User', related_name='comparison_items', on_delete=models.CASCADE)
    product = models.ForeignKey('products.Product', related_name='products_in_comparison',  on_delete=models.CASCADE)

    class Meta(BaseModel.Meta):
        verbose_name = 'Comparison'
        permission_basename = 'comparison'
        permissions = (
            ('get.comparison', 'مشاهده آیتم های مقایسه'),
            ('create.comparison', 'تعریف آیتم های مقایسه'),
            ('update.comparison', 'ویرایش آیتم های مقایسه'),
            ('delete.comparison', 'حذف آیتم های مقایسه'),

            ('getOwn.comparison', 'مشاهده آیتم های مقایسه خود'),
            ('updateOwn.comparison', 'ویرایش آیتم های مقایسه خود'),
            ('deleteOwn.comparison', 'حذف آیتم های مقایسه خود'),
        )

    def __str__(self):
        return "محصول {} در مقایسه های {}".format(self.product.name, self.customer.name)


class ShipmentAddress(BaseModel):
    customer = models.ForeignKey('users.User', related_name='shipment_address', on_delete=models.CASCADE)
    country = models.CharField(max_length=100, default='ایران')
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)
    address = models.CharField(max_length=255)

    class Meta(BaseModel.Meta):
        verbose_name = 'ShipmentAddress'
        permission_basename = 'shipment_address'
        permissions = (
            ('get.shipment_address', 'مشاهده آدرس'),
            ('create.shipment_address', 'تعریف آدرس'),
            ('update.shipment_address', 'ویرایش آدرس'),
            ('delete.shipment_address', 'حذف آدرس'),

            ('getOwn.shipment_address', 'مشاهده آدرس های خود'),
            ('updateOwn.shipment_address', 'ویرایش آدرس های خود'),
            ('deleteOwn.shipment_address', 'حذف آدرس های خود'),
        )

    def __str__(self):
        return "آدرس {} {}".format(self.city, self.customer.name)


class Payment(BaseModel):
    customer = models.ForeignKey('users.User', related_name='shop_payments', on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=100)
    tracking_code = models.CharField(max_length=50)
    amount = DECIMAL()
    date_time = models.DateTimeField(blank=True, null=True)

    class Meta(BaseModel.Meta):
        verbose_name = 'Payment'
        permission_basename = 'payment'
        permissions = (
            ('get.payment', 'مشاهده پرداخت'),
            ('create.payment', 'تعریف پرداخت'),
            ('update.payment', 'ویرایش پرداخت'),
            ('delete.payment', 'حذف پرداخت'),

            ('getOwn.payment', 'مشاهده پرداخت های خود'),
            ('updateOwn.payment', 'ویرایش پرداخت های خود'),
            ('deleteOwn.payment', 'حذف پرداخت های خود'),
        )

    def __str__(self):
        return "پرداخت {} {}".format(self.tracking_code, self.customer.name)


class ShopOrder(BaseModel):
    customer = models.ForeignKey('users.User', related_name='shop_order', on_delete=models.PROTECT)
    total_price = DECIMAL()
    total_product_quantity = DECIMAL(default=1)
    offer_price = DECIMAL(default=0)
    date_time = models.DateTimeField(blank=True, null=True)
    is_paid = models.BooleanField(default=False)
    payment = models.OneToOneField(Payment, related_name='shop_order', on_delete=models.PROTECT, blank=True, null=True)
    is_sent = models.BooleanField(default=False)
    shipment_address = models.ForeignKey(ShipmentAddress, related_name='shop_orders', on_delete=models.PROTECT)
    post_price = DECIMAL(blank=True, null=True)
    post_date_time = models.DateTimeField(blank=True, null=True)
    post_tracking_code = models.CharField(max_length=50, blank=True, null=True)
    exuni_tracking_code = models.CharField(max_length=10, unique=True)

    class Meta(BaseModel.Meta):
        verbose_name = 'ShopOrder'
        permission_basename = 'shop_order'
        permissions = (
            ('get.shop_order', 'مشاهده سفارش فروشگاه'),
            ('create.shop_order', 'تعریف سفارش فروشگاه'),
            ('update.shop_order', 'ویرایش سفارش فروشگاه'),
            ('delete.shop_order', 'حذف سفارش فروشگاه'),

            ('getOwn.shop_order', 'مشاهده سفارش های فروشگاه خود'),
            ('updateOwn.shop_order', 'ویرایش سفارش های فروشگاه خود'),
            ('deleteOwn.shop_order', 'حذف سفارش های فروشگاه خود'),
        )

    def add_cart_to_order(self):
        cart_items = Cart.objects.filter(customer=self.customer).select_related('product')
        for item in cart_items:
            ShopOrderItem.objects.create(
                shop_order=self,
                product=item.product,
                price=item.product.last_price * item.quantity,
                price_sum=item.product.last_price * item.quantity,
                product_quantity=item.quantity,
            )
            item.delete()

    def set_constants(self):
        items = self.items.all().annotate(
            price_sum=Sum(F('product_quantity') * F('price'), output_field=DecimalField()),
        ).aggregate(Sum('price_sum'), Sum('product_quantity'))
        self.total_price = items['price_sum__sum']
        self.total_product_quantity = items['product_quantity__sum']
        self.save()


    @property
    def create_exuni_tracking_code(self):
        create_exuni_tracking_code = random.randint(1000000000, 9999999999)
        while ShopOrder.objects.filter(product_id=create_exuni_tracking_code).exists():
            create_exuni_tracking_code = random.randint(1000000000, 9999999999)
        return str(create_exuni_tracking_code)

    def __str__(self):
        return "سفارش {} {}".format(self.exuni_tracking_code, self.customer.name)

    def save(self, *args, **kwargs):
        if not self.id:
            self.exuni_tracking_code = self.create_exuni_tracking_code
        super().save(*args, **kwargs)


class ShopOrderItem(BaseModel):
    shop_order = models.ForeignKey(ShopOrder, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey('products.Product', related_name='shop_order_items',  on_delete=models.CASCADE)
    price = DECIMAL(default=0)
    product_quantity = DECIMAL(default=1)

    class Meta(BaseModel.Meta):
        verbose_name = 'ShopOrderItem'
        permission_basename = 'shop_order_item'
        permissions = (
            ('get.shop_order_item', 'مشاهده آیتم های سفارش فروشگاه'),
            ('create.shop_order_item', 'تعریف آیتم های سفارش فروشگاه'),
            ('update.shop_order_item', 'ویرایش آیتم های سفارش فروشگاه'),
            ('delete.shop_order_item', 'حذف آیتم های سفارش فروشگاه'),

            ('getOwn.shop_order_item', 'مشاهده آیتم های سفارش های فروشگاه خود'),
            ('updateOwn.shop_order_item', 'ویرایش آیتم های سفارش های فروشگاه خود'),
            ('deleteOwn.shop_order_item', 'حذف آیتم های سفارش های فروشگاه خود'),
        )

    @property
    def price_sum(self):
        return self.price * self.product_quantity

    def __str__(self):
        return "آیتم های سفارش {} {}".format(self.shop_order.exuni_tracking_code, self.customer.name)


class Comment(BaseModel):
    customer = models.ForeignKey('users.User', related_name='comments', on_delete=models.CASCADE)
    product = models.ForeignKey('products.Product', related_name='product_comments',  on_delete=models.CASCADE,
                                blank=True, null=True)
    shop_order = models.ForeignKey(ShopOrder, related_name='comments',  on_delete=models.CASCADE,
                                   blank=True, null=True)
    date_time = models.DateTimeField(blank=True, null=True)
    reply = models.ForeignKey('self', related_name='replies',  on_delete=models.CASCADE)
    text = models.TextField()

    confirmed = models.BooleanField(default=False)

    class Meta(BaseModel.Meta):
        verbose_name = 'Comment'
        permission_basename = 'comment'
        permissions = (
            ('get.comment', 'مشاهده کامنت'),
            ('create.comment', 'تعریف کامنت'),
            ('update.comment', 'ویرایش کامنت'),
            ('delete.comment', 'حذف کامنت'),

            ('getOwn.comment', 'مشاهده کامنت های خود'),
            ('updateOwn.comment', 'ویرایش کامنت های خود'),
            ('deleteOwn.comment', 'حذف کامنت های خود'),
        )


class Rate(BaseModel):
    ONE_STAR = 1
    TWO_STAR = 2
    THREE_STAR = 3
    FOUR_STAR = 4
    FIVE_STAR = 5

    RATES_LEVELS = (
        (ONE_STAR, 'یک ستاره'),
        (TWO_STAR, 'دو ستاره'),
        (THREE_STAR, 'سه ستاره'),
        (FOUR_STAR, 'چهار ستاره'),
        (FIVE_STAR, 'پنج ستاره'),
    )

    customer = models.ForeignKey('users.User', related_name='rates', on_delete=models.CASCADE)
    product = models.ForeignKey('products.Product', related_name='products_rates',  on_delete=models.CASCADE)
    level = models.IntegerField(choices=RATES_LEVELS, default=FIVE_STAR)

    class Meta(BaseModel.Meta):
        verbose_name = 'Rate'
        permission_basename = 'rate'
        permissions = (
            ('get.rate', 'مشاهده امتیاز'),
            ('create.rate', 'تعریف امتیاز'),
            ('update.rate', 'ویرایش امتیاز'),
            ('delete.rate', 'حذف امتیاز'),

            ('getOwn.rate', 'مشاهده امتیاز های خود'),
            ('updateOwn.rate', 'ویرایش امتیاز های خود'),
            ('deleteOwn.rate', 'حذف امتیاز های خود'),
        )

    def save(self, *args, **kwargs):
        if not self.id and Rate.objects.filter(Q(customer=self.customer) & Q(product=self.product)).exists():
            raise ValidationError('Customer satisfaction rate already exist for this product')
        super().save(*args, **kwargs)


class LimitedTimeOffer(BaseModel):
    PERCENTAGE_OFFER = 'p'
    AMOUNT_OFFER = 'a'
    NONE = 'n'

    OFFER_TYPES = (
        (PERCENTAGE_OFFER, 'تخفیف درصدی'),
        (AMOUNT_OFFER, 'تخفیف مبلغی'),
        (NONE, 'هیچ کدام'),
    )

    offer_type = models.CharField(max_length=1, default=NONE)
    name = models.CharField(max_length=255, default='فروش ویژه')
    description = models.TextField(blank=True, null=True)
    from_date_time = models.DateTimeField(blank=True, null=True)
    to_date_time = models.DateTimeField(blank=True, null=True)

    class Meta(BaseModel.Meta):
        verbose_name = 'LimitedTimeOffer'
        permission_basename = 'limited_time_offer'
        permissions = (
            ('get.limited_time_offer', 'مشاهده فروش ویژه به مدت محدود'),
            ('create.limited_time_offer', 'تعریف فروش ویژه به مدت محدود'),
            ('update.limited_time_offer', 'ویرایش فروش ویژه به مدت محدود'),
            ('delete.limited_time_offer', 'حذف فروش ویژه به مدت محدود'),

            ('getOwn.limited_time_offer', 'مشاهده فروش های ویژه به مدت محدود خود'),
            ('updateOwn.limited_time_offer', 'ویرایش فروش های ویژه به مدت محدود خود'),
            ('deleteOwn.limited_time_offer', 'حذف فروش های ویژه به مدت محدود خود'),
        )

    def __str__(self):
        return "{} از {} تا {}".format(
            self.name, datetime_to_str(self.from_date_time), datetime_to_str(self.to_date_time)
        )


class LimitedTimeOfferItems(BaseModel):
    PERCENTAGE_OFFER = 'p'
    AMOUNT_OFFER = 'a'

    OFFER_TYPES = (
        (PERCENTAGE_OFFER, 'تخفیف درصدی'),
        (AMOUNT_OFFER, 'تخفیف مبلغی'),
    )
    limited_time_offer = models.ForeignKey(LimitedTimeOffer, related_name='items',  on_delete=models.CASCADE)
    offer_type = models.CharField(max_length=1, default=PERCENTAGE_OFFER)
    digit = DECIMAL()
    product = models.ForeignKey('products.Product', related_name='offers',  on_delete=models.CASCADE)

    class Meta(BaseModel.Meta):
        verbose_name = 'LimitedTimeOfferItems'
        permission_basename = 'limited_time_offer_items'
        permissions = (
            ('get.limited_time_offer_items', 'مشاهده آیتم فروش ویژه به مدت محدود'),
            ('create.limited_time_offer_items', 'تعریف آیتم فروش ویژه به مدت محدود'),
            ('update.limited_time_offer_items', 'ویرایش آیتم فروش ویژه به مدت محدود'),
            ('delete.limited_time_offer_items', 'حذف آیتم فروش ویژه به مدت محدود'),

            ('getOwn.limited_time_offer_items', 'مشاهده آیتم های فروش ویژه به مدت محدود خود'),
            ('updateOwn.limited_time_offer_items', 'ویرایش آیتم های فروش های ویژه به مدت محدود خود'),
            ('deleteOwn.limited_time_offer_items', 'حذف آیتم های فروش های ویژه به مدت محدود خود'),
        )

    @property
    def price_after_offer(self):
        if self.offer_type == self.AMOUNT_OFFER:
            return self.product.last_price - self.digit
        else:
            product_price = self.product.last_price
            offer_amount = product_price / 100 * self.digit
            return product_price - offer_amount

    @property
    def offer_amount(self):
        if self.offer_type == self.AMOUNT_OFFER:
            return self.digit
        else:
            offer_amount = self.product.last_price / 100 * self.digit
            return offer_amount

    @property
    def offer_display(self):
        if self.offer_type == self.AMOUNT_OFFER:
            return ' {} تومان تخفیف'.format(add_separator(self.digit))
        else:
            return ' {}% تخفیف'.format(self.digit)

