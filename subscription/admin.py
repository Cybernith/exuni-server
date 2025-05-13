from django.contrib import admin

# Register your models here.
from subscription.models import Wallet, Transaction, DiscountCode, Factor, FactorItem

admin.site.register(Wallet)
admin.site.register(Transaction)
admin.site.register(DiscountCode)
admin.site.register(Factor)
admin.site.register(FactorItem)
