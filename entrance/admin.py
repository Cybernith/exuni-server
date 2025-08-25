from django.contrib import admin

from entrance.models import EntrancePackage, EntrancePackageItem, StoreReceipt, StoreReceiptItem, \
    EntrancePackageFileColumn, ChinaEntrancePackage, ChinaEntrancePackageItem

admin.site.register(EntrancePackage)
admin.site.register(EntrancePackageItem)
admin.site.register(EntrancePackageFileColumn)
admin.site.register(StoreReceipt)
admin.site.register(StoreReceiptItem)
admin.site.register(ChinaEntrancePackage)
admin.site.register(ChinaEntrancePackageItem)
