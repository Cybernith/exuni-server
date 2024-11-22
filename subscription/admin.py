from django.contrib import admin

# Register your models here.
from subscription.models import Plan, Wallet, Extension, Transaction, DiscountCode, CompanyExtension

admin.site.register(Plan)
admin.site.register(Extension)
admin.site.register(CompanyExtension)
admin.site.register(Wallet)
admin.site.register(Transaction)
admin.site.register(DiscountCode)
