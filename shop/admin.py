from django.contrib import admin

from shop.models import Cart, WishList, Comparison, Comment, Rate, LimitedTimeOffer, LimitedTimeOfferItems, \
    ShipmentAddress, ShopOrder, ShopOrderItem, ShopOrderStatusHistory, ShippingMethod
from nested_admin import NestedModelAdmin, NestedStackedInline
from django.utils.html import format_html
from subscription.models import DiscountCode

admin.site.register(Cart)
admin.site.register(WishList)
admin.site.register(Comparison)
admin.site.register(Comment)
admin.site.register(Rate)
admin.site.register(LimitedTimeOffer)
admin.site.register(LimitedTimeOfferItems)
admin.site.register(ShipmentAddress)
admin.site.register(ShopOrderItem)
admin.site.register(ShippingMethod)


@admin.register(ShopOrderStatusHistory)
class ShopOrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['shop_order', 'previous_status', 'new_status', 'changed_at', 'changed_by']
    list_filter = ['new_status', 'changed_at', 'changed_by']
    search_fields = ['shop_order__id', 'changed_by__username']

class ShopOrderStatusHistoryInline(NestedStackedInline):
    model = ShopOrderStatusHistory
    extra = 0
    fields = ['previous_status', 'new_status', 'changed_at', 'changed_by', 'note']
    readonly_fields = ['previous_status', 'new_status', 'changed_at']
    autocomplete_fields = ['changed_by']
    can_delete = False

class ShopOrderItemInline(NestedStackedInline):
    model = ShopOrderItem
    extra = 1
    fields = ['product', 'picture_preview', 'price', 'product_quantity', 'price_sum']
    readonly_fields = ['price_sum', 'picture_preview']
    autocomplete_fields = ['product']

    def picture_preview(self, obj):
        if obj.product and obj.product.picture:
            return format_html('<img src="{}" style="max-height: 100px;" />', obj.product.picture.url)
        return "-"
    picture_preview.short_description = "پیش‌نمایش تصویر محصول"

    def price_sum(self, obj):
        return obj.price_sum
    price_sum.short_description = "جمع قیمت"


@admin.register(ShopOrder)
class ShopOrderAdmin(NestedModelAdmin):
    list_display = [
        'exuni_tracking_code', 'customer', 'status_display', 'total_price',
        'final_amount', 'date_time', 'is_sent'
    ]
    list_filter = ['status', 'date_time', 'is_sent']
    search_fields = ['exuni_tracking_code', 'customer__name', 'post_tracking_code']
    inlines = [ShopOrderItemInline, ShopOrderStatusHistoryInline]
    fields = [
        'exuni_tracking_code', 'customer', 'status', 'total_price', 'total_product_quantity',
        'offer_price', 'discount_code', 'discount_amount', 'total_discount',
        'shipment_address', 'shipping_method', 'post_price', 'post_date_time',
        'post_tracking_code', 'is_sent', 'date_time', 'final_amount'
    ]
    readonly_fields = ['exuni_tracking_code', 'total_price', 'total_product_quantity', 'final_amount']
    autocomplete_fields = ['customer', 'shipment_address', 'shipping_method', 'discount_code']
    date_hierarchy = 'date_time'

    def status_display(self, obj):
        return obj.get_status_display()
    status_display.short_description = "وضعیت"

    def final_amount(self, obj):
        return obj.final_amount
    final_amount.short_description = "مبلغ نهایی"

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related(
            'items', 'history', 'customer', 'shipment_address', 'shipping_method', 'discount_code'
        )
