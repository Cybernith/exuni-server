from django.contrib import admin

from entrance.models import EntrancePackage, EntrancePackageItem, StoreReceipt, StoreReceiptItem

admin.site.register(EntrancePackage)
admin.site.register(EntrancePackageItem)
admin.site.register(StoreReceipt)
admin.site.register(StoreReceiptItem)
