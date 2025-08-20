from django.contrib import admin

from store_handle.models import ProductStoreInventory, ProductStoreInventoryHistory, ProductStoreInventoryHandle, \
    ProductPackingInventoryHandle, ProductHandleChange, ShippingBox, TransferToPackingRequest, InventoryTransfer

admin.site.register(TransferToPackingRequest)
admin.site.register(ProductStoreInventory)
admin.site.register(ProductStoreInventoryHistory)
admin.site.register(ProductStoreInventoryHandle)
admin.site.register(ProductPackingInventoryHandle)
admin.site.register(ProductHandleChange)
admin.site.register(ShippingBox)
admin.site.register(InventoryTransfer)
