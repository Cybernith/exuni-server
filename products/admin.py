from django.contrib import admin
from django.utils.html import format_html
from nested_admin import NestedModelAdmin, NestedStackedInline

from products.models import Brand, Avail, ProductProperty, Category, Product, ProductGallery, ProductInventory, \
    ProductPrice, ProductPriceHistory, ProductInventoryHistory, ProductPropertyTerm, ProductAttribute, \
    ProductAttributeTerm

admin.site.register(Avail)
admin.site.register(ProductProperty)
admin.site.register(ProductPropertyTerm)
admin.site.register(ProductAttribute)
admin.site.register(ProductAttributeTerm)
admin.site.register(Category)
admin.site.register(ProductGallery)


class ProductVariationInline(NestedStackedInline):
    model = Product
    extra = 1
    fk_name = 'variation_of'
    fields = [
        'name', 'variation_title', 'product_type', 'product_id',
        'picture', 'picture_preview', 'price', 'regular_price', 'calculate_current_inventory'
    ]
    readonly_fields = ['picture_preview']
    autocomplete_fields = ['brand']

    def picture_preview(self, obj):
        if obj.picture:
            return format_html('<img src="{}" style="max-height: 100px;" />', obj.picture.url)
        return "-"
    picture_preview.short_description = "پیش‌نمایش تصویر اصلی"

@admin.register(Product)
class ProductAdmin(NestedModelAdmin):
    list_display = [
        'id', 'name', 'product_type', 'picture_preview', 'regular_price', 'price',
        'offer_percentage', 'calculate_current_inventory', 'brand'
    ]
    list_filter = ['status', 'product_type', 'brand']
    search_fields = ['name', 'product_id', 'sixteen_digit_code']
    inlines = [ProductVariationInline]
    fields = [
        'id', 'product_type', 'name', 'picture', 'picture_preview',
        'regular_price', 'price', 'offer_percentage', 'calculate_current_inventory',
        'brand', 'price_title', 'regular_price_title'
    ]
    readonly_fields = ['picture_preview', 'price_title', 'regular_price_title', 'calculate_current_inventory']
    autocomplete_fields = ['brand']

    def picture_preview(self, obj):
        if obj.picture:
            return format_html('<img src="{}" style="max-height: 100px;" />', obj.picture.url)
        return "-"
    picture_preview.short_description = "تصویر اصلی"

    def price_title(self, obj):
        return self.get_price_title(obj)
    price_title.short_description = "عنوان قیمت"

    def regular_price_title(self, obj):
        return self.get_regular_price_title(obj)
    regular_price_title.short_description = "عنوان قیمت اصلی"

    def offer_percentage(self, obj):
        return self.get_offer_percentage(obj)
    offer_percentage.short_description = "درصد تخفیف"

    def get_price_title(self, obj):
        return 'قیمت در اکسونی'

    def get_regular_price_title(self, obj):
        if obj.brand and obj.brand.made_in:
            if obj.brand.made_in == 'ایران':
                return 'قیمت مصرف کننده'
        return 'قیمت محصول'

    def get_offer_percentage(self, obj):
        if obj.regular_price and obj.price:
            offer_percentage = round(((obj.regular_price - obj.price) / obj.regular_price) * 100)
            return f'{offer_percentage}%'
        return None

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('brand', 'variations')

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    search_fields = ['name']


@admin.register(ProductPrice)
class ProductPriceAdmin(admin.ModelAdmin):
    list_display = ['product', 'price', 'last_updated']


@admin.register(ProductPriceHistory)
class ProductPriceHistoryAdmin(admin.ModelAdmin):
    list_display = ['product', 'previous_price', 'new_price', 'changed_at', 'changed_by']
    list_filter = ['product', 'changed_at', 'changed_by']
    search_fields = ['product__name']


@admin.register(ProductInventory)
class ProductInventoryAdmin(admin.ModelAdmin):
    list_display = ['product', 'inventory', 'last_updated']


@admin.register(ProductInventoryHistory)
class ProductInventoryHistoryAdmin(admin.ModelAdmin):
    list_display = ['inventory', 'previous_quantity', 'new_quantity', 'timestamp', 'changed_by']
    list_filter = ['inventory', 'timestamp', 'changed_by']
    search_fields = ['inventory']
