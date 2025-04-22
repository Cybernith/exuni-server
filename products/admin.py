from django.contrib import admin

from products.models import Brand, Avail, ProductProperty, Category, Product, ProductGallery, ProductInventory, \
    ProductPrice, ProductPriceHistory

admin.site.register(Brand)
admin.site.register(Avail)
admin.site.register(ProductProperty)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(ProductInventory)
admin.site.register(ProductGallery)


@admin.register(ProductPrice)
class ProductPriceAdmin(admin.ModelAdmin):
    list_display = ['product', 'price', 'last_updated']


@admin.register(ProductPriceHistory)
class ProductPriceHistoryAdmin(admin.ModelAdmin):
    list_display = ['product', 'previous_price', 'new_price', 'changed_at', 'changed_by']
    list_filter = ['product', 'changed_at', 'changed_by']
    search_fields = ['product__name']
