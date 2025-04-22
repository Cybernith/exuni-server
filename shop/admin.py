from django.contrib import admin

from shop.models import Cart, WishList, Comparison, Comment, Rate, LimitedTimeOffer, LimitedTimeOfferItems, \
    ShipmentAddress, Payment, ShopOrder, ShopOrderItem, ShopOrderStatusHistory

admin.site.register(Cart)
admin.site.register(WishList)
admin.site.register(Comparison)
admin.site.register(Comment)
admin.site.register(Rate)
admin.site.register(LimitedTimeOffer)
admin.site.register(LimitedTimeOfferItems)
admin.site.register(ShipmentAddress)
admin.site.register(Payment)
admin.site.register(ShopOrder)
admin.site.register(ShopOrderItem)


@admin.register(ShopOrderStatusHistory)
class ShopOrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['shop_order', 'previous_status', 'new_status', 'changed_at', 'changed_by']
    list_filter = ['new_status', 'changed_at', 'changed_by']
    search_fields = ['shop_order__id', 'changed_by__username']
