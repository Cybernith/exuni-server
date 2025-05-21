from django.contrib import admin
from nested_admin import NestedModelAdmin, NestedStackedInline
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.utils import timezone
from cms.models import HeaderElement, PopUpElement, BannerContent, BannerContentItem, ShopHomePageStory, \
    ShopHomeHighlight, ShopHomeHighlightItem
from subscription.models import DiscountCode


admin.site.register(HeaderElement)
admin.site.register(PopUpElement)
admin.site.register(ShopHomePageStory)



@admin.register(DiscountCode)
class DiscountCodeAdmin(admin.ModelAdmin):
    list_display = ('code',)  # فرض بر اینه که DiscountCode یه فیلد code داره
    search_fields = ('code',)  # برای autocomplete_fields
    list_filter = ('code',)
    verbose_name = _("کد تخفیف")
    verbose_name_plural = _("کدهای تخفیف")

class BannerContentItemInline(NestedStackedInline):
    model = BannerContentItem
    extra = 1
    min_num = 0
    max_num = 10
    fields = (
        'title',
        'description',
        'mobile_image',
        'desktop_image',
        'link',
        'discount_code'
    )
    autocomplete_fields = ['discount_code']
    readonly_fields = ['banner_content']
    verbose_name = _("آیتم محتوای بنر")
    verbose_name_plural = _("آیتم‌های محتوای بنر")

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        formset.form.base_fields['mobile_image'].widget.attrs.update({
            'class': 'file-upload',
            'accept': 'image/*'
        })
        formset.form.base_fields['desktop_image'].widget.attrs.update({
            'class': 'file-upload',
            'accept': 'image/*'
        })
        return formset

# ادمین برای BannerContent
@admin.register(BannerContent)
class BannerContentAdmin(NestedModelAdmin):
    inlines = [BannerContentItemInline]
    list_display = (
        'title',
        'order_display',
        'auto_scroll_seconds',
        'from_date_time',
        'to_date_time',
    )
    list_filter = (
        'order',
        'from_date_time',
        'to_date_time',
        ('items__discount_code', admin.RelatedOnlyFieldListFilter)
    )
    search_fields = ('title',)
    list_editable = ('auto_scroll_seconds',)
    list_per_page = 20
    fieldsets = (
        (_('اطلاعات اصلی'), {
            'fields': ('title', 'order', 'auto_scroll_seconds')
        }),
        (_('بازه زمانی'), {
            'fields': ('from_date_time', 'to_date_time')
        }),
    )
    date_hierarchy = 'from_date_time'
    ordering = ('-from_date_time',)

    def order_display(self, obj):
        return dict(BannerContent.ORDERS).get(obj.order, obj.order)
    order_display.short_description = _("ترتیب")

    def is_active(self, obj):
        from django.utils import timezone
        now = timezone.now()
        return obj.from_date_time <= now <= obj.to_date_time
    is_active.short_description = _("فعال")
    is_active.boolean = True

# ادمین برای BannerContentItem
@admin.register(BannerContentItem)
class BannerContentItemAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'banner_content',
        'link',
        'discount_code',
        'has_images'
    )
    list_filter = ('banner_content', 'discount_code')
    search_fields = ('title', 'link', 'description')
    list_per_page = 20
    fields = (
        'banner_content',
        'title',
        'description',
        'mobile_image',
        'desktop_image',
        'link',
        'discount_code'
    )
    autocomplete_fields = ['banner_content', 'discount_code']
    ordering = ('banner_content',)

    def has_images(self, obj):
        return bool(obj.mobile_image and obj.desktop_image)
    has_images.short_description = _("دارای تصویر")
    has_images.boolean = True


class ShopHomeHighlightItemInline(NestedStackedInline):
    model = ShopHomeHighlightItem
    extra = 1
    fields = [
        'title', 'type', 'category', 'brand',
        'mobile_image', 'desktop_image', 'mobile_image_preview', 'desktop_image_preview',
        'from_date_time', 'to_date_time'
    ]
    search_fields = ['name', 'id']
    readonly_fields = ['mobile_image_preview', 'desktop_image_preview']

    def mobile_image_preview(self, obj):
        if obj.mobile_image:
            return format_html('<img src="{}" style="max-height: 100px;" />', obj.mobile_image.url)
        return "-"
    mobile_image_preview.short_description = "پیش‌نمایش تصویر موبایل"

    def desktop_image_preview(self, obj):
        if obj.desktop_image:
            return format_html('<img src="{}" style="max-height: 100px;" />', obj.desktop_image.url)
        return "-"
    desktop_image_preview.short_description = "پیش‌نمایش تصویر دسکتاپ"


@admin.register(ShopHomeHighlight)
class ShopHomeHighlightAdmin(NestedModelAdmin):
    list_display = ['title', 'from_date_time', 'to_date_time', 'is_active', 'item_count']
    list_filter = ['from_date_time', 'to_date_time']
    search_fields = ['title', 'description']
    inlines = [ShopHomeHighlightItemInline]
    fields = ['title', 'description', 'from_date_time', 'to_date_time']
    date_hierarchy = 'from_date_time'

    def is_active(self, obj):
        now = timezone.now()
        return obj.from_date_time <= now <= obj.to_date_time
    is_active.short_description = "فعال"
    is_active.boolean = True

    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = "تعداد آیتم‌ها"

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('items')