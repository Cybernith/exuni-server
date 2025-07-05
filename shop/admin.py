from django.contrib import admin

from helpers.functions import datetime_to_str
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


class MobileNumberFilter(admin.SimpleListFilter):
    title = 'Mobile Number'
    parameter_name = 'mobile'

    def lookups(self, request, model_admin):
        return [
            ('exact', 'Exact Match'),
            ('contains', 'Contains'),
        ]

    def queryset(self, request, queryset):
        value = request.GET.get('mobile_number')
        if not value:
            return queryset

        if self.value() == 'exact':
            return queryset.filter(customer__mobile_number=value)
        elif self.value() == 'contains':
            return queryset.filter(customer__mobile_number__icontains=value)
        return queryset


class MobileNumberExactFilter(admin.SimpleListFilter):
    title = 'Mobile (Exact)'
    parameter_name = 'mobile_number'

    def lookups(self, request, model_admin):
        mobiles = set()
        for order in ShopOrder.objects.all().select_related('customer'):
            if order.customer and order.customer.mobile_number:
                mobiles.add((order.customer.mobile_number, order.customer.mobile_number))
        return sorted(mobiles, key=lambda x: x[1])

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(customer__mobile_number=self.value())
        return queryset


@admin.register(ShopOrder)
class ShopOrderAdmin(admin.ModelAdmin):
    def get_jalali_date_time(self, obj):
        if obj.date_time:
            return datetime_to_str(obj.date_time)

    list_display = (
        'exuni_tracking_code',
        'customer_info',
        'status_display',
        'total_price',
        'total_discount',
        'discount_amount',
        'post_price',
        'final_amount_display',
        'get_jalali_date_time',
        'is_sent',
    )

    list_filter = (
        'status',
        'is_sent',
        MobileNumberExactFilter,  # Dropdown with exact numbers
        MobileNumberFilter,      # Exact/Contains selector
        'date_time',
    )

    search_fields = (
        'exuni_tracking_code',
        'customer__mobile_number',
        'customer__first_name',  # Changed from 'name' to actual field name
        'customer__last_name',  # Add if you have last name field
        'post_tracking_code',
    )

    raw_id_fields = ('customer', 'shipment_address', 'shipping_method', 'discount_code')

    readonly_fields = (
        'final_amount_display',
        'exuni_tracking_code',
        'post_date_time',
    )

    fieldsets = (
        ('Basic Information', {
            'fields': (
                'exuni_tracking_code',
                'customer',
                'status',
                'date_time',
                'is_sent',
            )
        }),
        ('Pricing Information', {
            'fields': (
                'total_price',
                'offer_price',
                'total_discount',
                'discount_amount',
                'post_price',
                'final_amount_display',
            )
        }),
        ('Shipping Information', {
            'fields': (
                'shipment_address',
                'shipping_method',
                'post_tracking_code',
                'post_date_time',
            )
        }),
        ('Discount Information', {
            'fields': (
                'discount_code',
            )
        }),
    )

    def status_display(self, obj):
        return dict(obj.STATUS_CHOICES).get(obj.status, obj.status)

    status_display.short_description = 'Status'

    def customer_info(self, obj):
        return f"{obj.customer.name} ({obj.customer.mobile_number})"

    customer_info.short_description = 'Customer'
    customer_info.admin_order_field = 'customer__name'

    def final_amount_display(self, obj):
        return obj.final_amount

    final_amount_display.short_description = 'Final Amount'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related(
            'customer',
            'shipment_address',
            'shipping_method',
            'discount_code',
        )
        return queryset