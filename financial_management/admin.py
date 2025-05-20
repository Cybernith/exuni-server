from django.contrib import admin

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


class DiscountConditionCategoryInline(admin.StackedInline):
    model = DiscountConditionCategory
    extra = 0

class DiscountConditionBrandInline(admin.StackedInline):
    model = DiscountConditionBrand
    extra = 0

class DiscountConditionProductInline(admin.StackedInline):
    model = DiscountConditionProduct
    extra = 0

class DiscountConditionUserInline(admin.StackedInline):
    model = DiscountConditionUser
    extra = 0

class DiscountConditionPriceOverInline(admin.StackedInline):
    model = DiscountConditionPriceOver
    extra = 0

class DiscountConditionPriceLimitInline(admin.StackedInline):
    model = DiscountConditionPriceLimit
    extra = 0


@admin.register(DiscountCondition)
class DiscountConditionAdmin(admin.ModelAdmin):
    list_display = ('discount', 'type')
    inlines = [
        DiscountConditionCategoryInline,
        DiscountConditionBrandInline,
        DiscountConditionProductInline,
        DiscountConditionUserInline,
        DiscountConditionPriceOverInline,
        DiscountConditionPriceLimitInline,
    ]


class DiscountActionInline(admin.StackedInline):
    model = DiscountAction
    extra = 0


class DiscountConditionInline(admin.TabularInline):
    model = DiscountCondition
    extra = 0


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'start_date', 'end_date')
    search_fields = ('name',)
    inlines = [DiscountConditionInline, DiscountActionInline]


@admin.register(DiscountUsage)
class DiscountUsageAdmin(admin.ModelAdmin):
    list_display = ('discount', 'user', 'used_at')
    search_fields = ('user__mobile_number',)
