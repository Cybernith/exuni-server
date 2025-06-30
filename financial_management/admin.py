from django.contrib import admin
import nested_admin

from financial_management.models import Wallet, Transaction, WalletLedger, AuditAction, FinancialAuditLog, Payment, \
    AffiliateOrderPayment, DiscountConditionCategory, DiscountConditionBrand, DiscountConditionProduct, \
    DiscountConditionUser, DiscountConditionPriceOver, DiscountConditionPriceLimit, DiscountCondition, Discount, \
    DiscountAction, DiscountUsage
from helpers.functions import datetime_to_str

admin.site.register(WalletLedger)
admin.site.register(FinancialAuditLog)
admin.site.register(AffiliateOrderPayment)



@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        'get_jalali_created_at',
        'wallet_info',
        'type_display',
        'amount',
        'status_display',
        'shop_order_info',
        'transaction_for_display',
    )

    list_filter = (
        'type',
        'status',
        'transaction_for',
    )

    search_fields = (
        'wallet__user__mobile_number',
        'shop_order__exuni_tracking_code',
        'description',
    )

    readonly_fields = (
        'get_jalali_created_at',
        'wallet_info',
        'shop_order_info',
    )

    fieldsets = (
        ('Transaction Information', {
            'fields': (
                'type',
                'amount',
                'status',
                'transaction_for',
            )
        }),
        ('Related Information', {
            'fields': (
                'wallet',
                'shop_order',
                'description',
                'metadata',
            )
        }),
        ('System Information', {
            'fields': (
                'get_jalali_created_at',
            ),
            'classes': ('collapse',)
        }),
    )

    def wallet_info(self, obj):
        if obj.wallet.user:
            return f"User: {obj.wallet.user.mobile_number}"
        return f"Business: {obj.wallet.business.name}"

    wallet_info.short_description = 'Wallet Owner'

    def shop_order_info(self, obj):
        if obj.shop_order:
            return obj.shop_order.exuni_tracking_code
        return "-"

    shop_order_info.short_description = 'Order Tracking'

    def type_display(self, obj):
        return dict(obj.TRANSACTION_TYPE).get(obj.type, obj.type)

    type_display.short_description = 'Type'

    def status_display(self, obj):
        return dict(obj.TRANSACTION_STATUS).get(obj.status, obj.status)

    status_display.short_description = 'Status'

    def transaction_for_display(self, obj):
        return dict(obj.TRANSACTION_TYPE).get(obj.transaction_for, obj.transaction_for)

    transaction_for_display.short_description = 'Transaction For'

    def get_jalali_created_at(self, obj):
        if obj.created_at:
            return datetime_to_str(obj.created_at)


    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related(
            'shop_order'
        )
        return queryset


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
            return queryset.filter(user__mobile_number=value)
        elif self.value() == 'contains':
            return queryset.filter(user__mobile_number__icontains=value)
        return queryset


class MobileNumberExactFilter(admin.SimpleListFilter):
    title = 'Mobile (Exact)'
    parameter_name = 'mobile_number'

    def lookups(self, request, model_admin):
        mobiles = set()
        for wallet in Wallet.objects.all().select_related('user'):
            if wallet.user and wallet.user.mobile_number:
                mobiles.add((wallet.user.mobile_number, wallet.user.mobile_number))
        return sorted(mobiles, key=lambda x: x[1])

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(user__mobile_number=self.value())
        return queryset


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'balance',
        'is_active',
    )

    list_filter = (
        MobileNumberExactFilter,  # Dropdown with exact numbers
        MobileNumberFilter,  # Exact/Contains selector
        'is_active',
    )

    search_fields = (
        'user__mobile_number',
        'business__name',
    )

    fieldsets = (
        ('Wallet Information', {
            'fields': (
                'user',
                'balance',
            )
        }),
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('user', 'business')
        return queryset




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
            return self.readonly_fields + ('amount', 'user', 'business', 'shop_order')
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