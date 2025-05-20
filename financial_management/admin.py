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
admin.site.register(Payment)
admin.site.register(AffiliateOrderPayment)


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