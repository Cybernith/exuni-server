from django.db import transaction
from django.db.models import Sum, F

from products.models import ProductInventory, ProductInventoryHistory
from store_handle.models import ProductStoreInventory


class InventoryService:

    @staticmethod
    def get_total_inventory(product_id: int) -> int:
        packing_inventory = ProductInventory.objects.filter(product_id=product_id).aggregate(
            total=Sum("inventory")
        )["total"] or 0
        stores_inventory = ProductStoreInventory.objects.filter(product_id=product_id).aggregate(
            total=Sum("inventory")
        )["total"] or 0
        return packing_inventory + stores_inventory

    @staticmethod
    @transaction.atomic
    def update_product_total_inventory(product_id: int):
        total = InventoryService.get_total_inventory(product_id)
        ProductInventory.objects.filter(id=product_id).update(total_inventory=total)

    @staticmethod
    @transaction.atomic
    def transfer_inventory(product_id: int, from_store: int, to_store: int, quantity: int):
        from_product_inventory = ProductInventory.objects.select_for_update().get(
            product_id=product_id, store_id=from_store
        )
        to_product_inventory, _ = ProductInventory.objects.select_for_update().get_or_create(
            product_id=product_id, store_id=to_store
        )

        from_product_inventory.inventory = F("inventory") - quantity
        to_product_inventory.inventory = F("inventory") + quantity

        from_product_inventory.save(update_fields=["inventory"])
        to_product_inventory.save(update_fields=["inventory"])
