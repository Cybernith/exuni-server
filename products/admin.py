from django.contrib import admin

from products.models import Brand, Avail, ProductProperty, Category, Product, ProductGallery, ProductInventory

admin.site.register(Brand)
admin.site.register(Avail)
admin.site.register(ProductProperty)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(ProductInventory)
admin.site.register(ProductGallery)
