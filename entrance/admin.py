from django.contrib import admin

from entrance.models import EntrancePackage, EntrancePackageItem, StoreReceipt, StoreReceiptItem, \
    EntrancePackageFileColumn

admin.site.register(EntrancePackage)
admin.site.register(EntrancePackageItem)
admin.site.register(EntrancePackageFileColumn)
admin.site.register(StoreReceipt)
admin.site.register(StoreReceiptItem)
