from products.models import Product
from store_handle.models import ProductHandleChange, ProductStoreInventoryHandle


def apply_store_handling():
    products_change = ProductHandleChange.objects.filter(is_applied=False)
    products_store_inventory_handle = ProductStoreInventoryHandle.objects.filter(is_applied=False)

    for product_change in products_change:
        product_change.apply()

    for product_store_inventory_handle in products_store_inventory_handle:
        product_store_inventory_handle.aplly()


def apply_product_change(product_id):
    product = Product.objects.get(pk=product_id)
    changes = ProductHandleChange.objects.get(product=product, is_applied=False)
    changes.apply()


def apply_product_stores_inventory(product_id):
    product = Product.objects.get(pk=product_id)
    changes = ProductStoreInventoryHandle.objects.filter(product=product, is_applied=False)
    total_inventory = 0
    for change in changes:
        total_inventory += change.inventory
        change.apply()
        product.current_inventory.handle_inventory(val=total_inventory, user=change.changed_by)


