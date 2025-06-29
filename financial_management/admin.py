from django.contrib import admin
import nested_admin

from financial_management.models import Wallet, Transaction, WalletLedger, AuditAction, FinancialAuditLog, Payment, \
    AffiliateOrderPayment, DiscountConditionCategory, DiscountConditionBrand, DiscountConditionProduct, \
    DiscountConditionUser, DiscountConditionPriceOver, DiscountConditionPriceLimit, DiscountCondition, Discount, \
    DiscountAction, DiscountUsage

admin.site.register(Wallet)
admin.site.register(Transaction)
admin.site.register(WalletLedger)
admin.site.register(FinancialAuditLog)
admin.site.register(AffiliateOrderPayment)




@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    # List display configuration
    list_display = (
        'id',
        'get_status_display',
        'get_type_display',
        'user',
        'business',
        'amount',
        'used_amount_from_wallet',
        'gateway',
        'reference_id',
        'created_at',
        'paid_at',
    )

    # Fields to display in the form (add/edit)
    fieldsets = (
        (None, {
            'fields': (
                'type',
                'status',
                'user',
                'business',
                'shop_order',
                'amount',
                'used_amount_from_wallet',
                'gateway',
                'reference_id',
                'created_at',
                'paid_at',
            )
        }),
    )

    # Filter options
    list_filter = (
        'status',
        'type',
        'gateway',
        'created_at',
    )

    # Search fields
    search_fields = (
        'user__username',
        'user__email',
        'business__name',
        'reference_id',
        'shop_order__id',
    )

    # Raw ID fields for better performance with large datasets
    raw_id_fields = ('user', 'business', 'shop_order')

    # Date hierarchy for easy navigation
    date_hierarchy = 'created_at'

    # Default ordering
    ordering = ('-created_at',)

    # Make status and type human-readable in list view
    def get_status_display(self, obj):
        return dict(Payment.STATUS_CHOICES).get(obj.status, obj.status)

    get_status_display.short_description = 'Status'

    def get_type_display(self, obj):
        return dict(Payment.PAYMENT_TYPE_CHOICES).get(obj.type, obj.type)

    get_type_display.short_description = 'Type'

    # Readonly fields for certain statuses
    def get_readonly_fields(self, request, obj=None):
        if obj and obj.status in [Payment.SUCCESS, Payment.FAILED, Payment.EXPIRED, Payment.CANCELLED]:
            return self.readonly_fields + ('status', 'amount', 'user', 'business', 'shop_order')
        return self.readonly_fields

class DiscountConditionCategoryInline(nested_admin.NestedStackedInline):
    model = DiscountConditionCategory
    extra = 0

class DiscountConditionBrandInline(nested_admin.NestedStackedInline):
    model = DiscountConditionBrand
    extra = 0

class DiscountConditionProductInline(nested_admin.NestedStackedInline):
    model = DiscountConditionProduct
    extra = 0

class DiscountConditionUserInline(nested_admin.NestedStackedInline):
    model = DiscountConditionUser
    extra = 0

class DiscountConditionPriceOverInline(nested_admin.NestedStackedInline):
    model = DiscountConditionPriceOver
    extra = 0

class DiscountConditionPriceLimitInline(nested_admin.NestedStackedInline):
    model = DiscountConditionPriceLimit
    extra = 0


class DiscountConditionInline(nested_admin.NestedStackedInline):
    model = DiscountCondition
    extra = 0

    # اضافه کردن همه زیرشرط‌ها به عنوان inline تو در تو
    inlines = [
        DiscountConditionCategoryInline,
        DiscountConditionBrandInline,
        DiscountConditionProductInline,
        DiscountConditionUserInline,
        DiscountConditionPriceOverInline,
        DiscountConditionPriceLimitInline,
    ]

    # این بخش اختیاری: فقط Inline مرتبط با نوع شرط نمایش داده شود
    # اما برای سادگی می‌توان همه را نشان داد یا در فرم شرطی‌سازی کرد.

class DiscountActionInline(nested_admin.NestedStackedInline):
    model = DiscountAction
    extra = 0
    max_num = 1


@admin.register(Discount)
class DiscountAdmin(nested_admin.NestedModelAdmin):
    list_display = ('name', 'is_active', 'start_date', 'end_date')
    search_fields = ('name',)
    inlines = [DiscountConditionInline, DiscountActionInline]