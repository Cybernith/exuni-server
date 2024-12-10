from django.contrib import admin

from packing.models import OrderPackage, OrderPackageItem

admin.site.register(OrderPackage)
admin.site.register(OrderPackageItem)
