import datetime
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models, transaction, IntegrityError
from django.db.models import Q, Sum, F, DecimalField
from django.db.models.functions import Round, Least, TruncMinute
from django.utils import timezone

from financial_management.models import Payment, Discount, DiscountAction, DiscountUsage
from financial_management.serivces.discount_evaluator import evaluate_discount
from helpers.functions import datetime_to_str, add_separator
from helpers.models import BaseModel, DECIMAL, EXPLANATION
import random
from django_fsm import FSMField, transition

from location_field.models.plain import PlainLocationField

from shop.helpers import increase_inventory


class Cart(BaseModel):
    customer = models.ForeignKey('users.User', related_name='cart_items', on_delete=models.PROTECT)
    product = models.ForeignKey('products.Product', related_name='products_in_cart',  on_delete=models.PROTECT)
    quantity = models.IntegerField(default=1, validators=[MinValueValidator(1)])

    class Meta(BaseModel.Meta):
        verbose_name = 'Cart'
        permission_basename = 'cart'
        unique_together = ('customer', 'product')
        indexes = [
            models.Index(fields=['customer']),
            models.Index(fields=['product']),
        ]
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
        return f"محصول {self.product.name or '-'} در سبد {self.customer.get_full_name() or self.customer.username}"


class WishList(BaseModel):
    customer = models.ForeignKey('users.User', related_name='wish_list_items', on_delete=models.CASCADE)
    product = models.ForeignKey('products.Product', related_name='products_in_wish_list',  on_delete=models.CASCADE)

    class Meta(BaseModel.Meta):
        verbose_name = 'WishList'
        permission_basename = 'wish_list'
        unique_together = ('customer', 'product')
        indexes = [
            models.Index(fields=['customer']),
            models.Index(fields=['product']),
        ]
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
        unique_together = ('customer', 'product')
        indexes = [
            models.Index(fields=['customer']),
            models.Index(fields=['product']),
        ]

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
    address_title = models.CharField(max_length=255, blank=True, null=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    location = PlainLocationField(based_fields=['city'], zoom=7, blank=True, null=True)
    country = models.CharField(max_length=100, default='ایران')
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    house_number = models.CharField(max_length=255, blank=True, null=True)
    house_unit = models.CharField(max_length=255, blank=True, null=True)
    zip_code = models.CharField(
        max_length=10,
        validators=[
            RegexValidator(
                regex=r'^\d{10}$',
                message='کد پستی باید دقیقاً ۱۰ رقم باشد.',
                code='invalid_zip_code'
            )
        ]
        , blank=True, null=True
    )
    is_default = models.BooleanField(default=False)

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
        return f"آدرس در {self.city} - {self.full_name or 'بدون نام'}"

    @property
    def full_name(self):
        return f"{self.first_name or ''} {self.last_name or ''}".strip()


class ShippingMethod(models.Model):
    name = models.CharField(max_length=100)
    base_price = models.PositiveIntegerField(default=55000)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def calculate(self, order):
        return self.base_price

    class Meta(BaseModel.Meta):
        get_latest_by = 'created_at'


class ShopOrderManager(models.Manager):
    def get_queryset(self):
        qs = super().get_queryset().annotate(
            payable_amount=Round(F('total_price') - Least('discount_amount', 'total_price')),
            time=TruncMinute('created_at__time'),
        )
        return qs


class ShopOrder(BaseModel):
    PENDING = 'pe'
    PAID = 'pa'
    PROCESSING = 'pr'
    SHIPPED = 'sh'
    DELIVERED = 'de'
    RETURNS = 're'
    CANCELLED = 'ca'

    STATUS_CHOICES = (
        (PENDING, 'در انتظار پرداخت'),
        (PAID, 'جاری'),
        (PROCESSING, 'درحال بسته بندی'),
        (SHIPPED, 'ارسال شده'),
        (DELIVERED, 'تحویل شده'),
        (CANCELLED, 'لغو شده'),
        (RETURNS, 'مرجوعی'),
    )
    status = FSMField(choices=STATUS_CHOICES, default=PENDING, protected=False)
    customer = models.ForeignKey('users.User', related_name='shop_order', on_delete=models.PROTECT)
    total_price = DECIMAL(default=0)
    total_product_quantity = DECIMAL(default=1)
    offer_price = DECIMAL(default=0)
    date_time = models.DateTimeField(blank=True, null=True)
    is_sent = models.BooleanField(default=False)
    shipment_address = models.ForeignKey(ShipmentAddress, related_name='shop_orders', on_delete=models.PROTECT)
    shipping_method = models.ForeignKey(ShippingMethod, on_delete=models.SET_NULL, null=True)
    post_price = DECIMAL(blank=True, null=True)
    post_date_time = models.DateTimeField(blank=True, null=True)
    post_tracking_code = models.CharField(max_length=50, blank=True, null=True)
    exuni_tracking_code = models.CharField(max_length=10, unique=True)

    discount_code = models.ForeignKey('subscription.DiscountCode', on_delete=models.PROTECT, null=True, blank=True)
    discount_amount = DECIMAL(default=0)

    total_discount = DECIMAL(default=0)

    objects = ShopOrderManager()

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

    # FSM status change functions

    @transition(field='status', source=PENDING, target=PAID)
    def mark_as_paid(self):
        self.status = self.PAID
        self.save()

    @transition(field='status', source=PAID, target=PROCESSING)
    def process_order(self, user=None):
        self.status = self.PROCESSING
        self.save()

    @transition(field='status', source=PROCESSING, target=SHIPPED)
    def ship_order(self):
        self.status = self.SHIPPED
        self.save()

    @transition(field='status', source=SHIPPED, target=DELIVERED)
    def deliver_order(self):
        self.status = self.DELIVERED
        self.save()

    @transition(field='status', source='*', target=CANCELLED)
    def cancel_order(self):
        self.status = self.CANCELLED
        for item in self.items.all():
            increase_inventory(item.product.id, item.product_quantity)

        self.save()

    def apply_discounts_to_order(self):
        total_price = self.total_price
        total_discount = Decimal("0.00")
        free_shipping_applied = False

        cart_items = []
        for item in self.items.all():
            cart_items.append({
                "product": item.product,
                "quantity": item.product_quantity,
            })

        with transaction.atomic():
            self.order_discounts.all().delete()

            for discount in Discount.objects.filter(is_active=True):
                result = evaluate_discount(discount, cart_items, self.customer, total_price)
                if result:
                    discount_value = result['value'] or Decimal("0.00")
                    OrderDiscount.objects.create(
                        order=self,
                        discount=discount,
                        discount_value=discount_value,
                    )
                    DiscountUsage.objects.create(
                        discount=discount,
                        user=self.customer,
                    )
                    total_discount += discount_value

                    if result['type'] == DiscountAction.FREE_SHIPPING:
                        free_shipping_applied = True

            self.total_discount = total_discount

            if free_shipping_applied:
                self.post_price = Decimal("0.00")
            else:
                pass

            self.save()

    def get_discount_code_amount(self):
        if self.discount_code:
            discount_amount = (self.total_price + self.total_discount) * self.discount_code.discount_percentage / 100
            discount_amount = min(discount_amount, self.discount_code.max_discount_amount)
            return discount_amount
        return 0

    def set_constants(self):
        default_shipping_method = ShippingMethod.objects.earliest()
        items = self.items.all().annotate(
            price_sum=Sum(F('product_quantity') * F('price'), output_field=DecimalField()),
        ).aggregate(Sum('price_sum'), Sum('product_quantity'))
        self.total_price = items['price_sum__sum']
        self.total_product_quantity = items['product_quantity__sum']
        self.shipping_method = default_shipping_method
        self.post_price = default_shipping_method.calculate(self)
        self.apply_discounts_to_order()

        self.discount_amount = self.get_discount_code_amount()
        self.save()

    @property
    def final_amount(self):
        return max(
            (self.total_price - self.total_discount) - self.get_discount_code_amount() + self.post_price, Decimal(0)
        )

    def create_exuni_tracking_code(self):
        exuni_tracking_code = random.randint(1000000000, 9999999999)
        while ShopOrder.objects.filter(exuni_tracking_code=exuni_tracking_code).exists():
            exuni_tracking_code = random.randint(1000000000, 9999999999)
        return str(exuni_tracking_code)

    def pay_with_wallet(self, transaction_id=None):
        assert not self.status == self.PAID
        final_price = self.final_amount
        wallet = self.customer.exuni_wallet

        wallet_amount = wallet.balance
        used_from_wallet = min(wallet_amount, final_price)

        gateway_amount = final_price - used_from_wallet

        if gateway_amount > 0:
            payment = Payment.objects.create(
                shop_order=self,
                user=self.customer,
                amount=gateway_amount,
                used_amount_from_wallet=used_from_wallet,
                gateway='zarinpal',
                status=Payment.INITIATED,
                transaction_id=transaction_id,
                created_at=timezone.now()
            )
            payment.mark_as_pending(user=self.customer)
            return payment

        else:
            wallet.reduce_balance(
                shop_order=self, amount=used_from_wallet, transaction_id=transaction_id,
                description=f"پرداخت سفارش {self.exuni_tracking_code}"
            )
            wallet.refresh_from_db()
            self.mark_as_paid()
            return None

    def pay(self):
        assert not self.status == self.PAID

        discount_code = self.discount_code
        if discount_code:
            discount_code.use()

        self.set_constants()

        try:
            if self.bank_payment and self.bank_payment.status != 'su':
                    self.save()
                    self.bank_payment.mark_as_pending(user=self.customer)
                    return self.bank_payment
        except:
            payment = Payment.objects.create(
                shop_order=self,
                user=self.customer,
                type=Payment.FOR_SHOP_ORDER,
                amount=self.final_amount,
                gateway='zarinpal',
                status=Payment.INITIATED,
                created_at=timezone.now()
            )

            payment.mark_as_pending(user=self.customer)
            self.save()
            return payment


    def __str__(self):
        return "سفارش {} {}".format(self.exuni_tracking_code, self.customer.name)

    def save(self, *args, **kwargs):
        if not self.exuni_tracking_code:
            self.exuni_tracking_code = self.create_exuni_tracking_code()
        super().save(*args, **kwargs)


class ShopOrderStatusHistory(BaseModel):
    shop_order = models.ForeignKey(ShopOrder, related_name='history', on_delete=models.CASCADE)
    previous_status = models.CharField(choices=ShopOrder.STATUS_CHOICES, max_length=2)
    new_status = models.CharField(choices=ShopOrder.STATUS_CHOICES, max_length=2)
    changed_at = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, blank=True, null=True)
    note = EXPLANATION()

    class Meta:
        ordering = ['-changed_at']

    def __str__(self):
        return f"{self.shop_order} from {self.get_previous_status_display()} to {self.get_new_status_display()}"


class OrderDiscount(models.Model):
    order = models.ForeignKey(ShopOrder, related_name='order_discounts', on_delete=models.CASCADE)
    discount = models.ForeignKey('financial_management.Discount', on_delete=models.CASCADE)
    discount_value = models.DecimalField(max_digits=12, decimal_places=2)
    applied_at = models.DateTimeField(auto_now_add=True)


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
        return "آیتم های سفارش {} {}".format(self.shop_order.exuni_tracking_code, self.shop_order.customer.name)


class Comment(BaseModel):
    customer = models.ForeignKey('users.User', related_name='comments', on_delete=models.CASCADE)
    product = models.ForeignKey('products.Product', related_name='product_comments',  on_delete=models.CASCADE,
                                blank=True, null=True)
    shop_order = models.ForeignKey(ShopOrder, related_name='comments',  on_delete=models.CASCADE,
                                   blank=True, null=True)
    date_time = models.DateTimeField(blank=True, null=True)
    reply = models.ForeignKey('self', related_name='replies',  on_delete=models.CASCADE, null=True, blank=True)
    text = models.TextField(db_index=True)
    file = models.FileField(blank=True, null=True)

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
        unique_together = ('customer', 'product')
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
    is_active = models.BooleanField(default=False)

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

    @property
    def is_valid(self):
        now = datetime.datetime.now()
        start_validation = self.limited_time_offer.from_date_time >= now
        end_validation = self.limited_time_offer.to_date_time <= now
        return self.limited_time_offer.is_active and start_validation and end_validation
