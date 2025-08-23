from django.db import transaction
from django.db.models import F

from server.store_configs import PACKING_STORE_ID
from store_handle.models import ProductStoreInventory, ProductStoreInventoryHistory


class InventoryReservationService:

    @staticmethod
    @transaction.atomic
    def reserve_order(order):
        for item in order.items.all():
            packing_inventory, _ = ProductStoreInventory.objects.select_for_update().get_or_create(
                product=item.product,
                store_id=PACKING_STORE_ID,
                defaults={'inventory': 0, 'reserved_inventory': 0}
            )

            packing_inventory.reserved_inventory = F('reserved_inventory') + item.product_quantity
            packing_inventory.save(update_fields=['reserved_inventory'])

    @staticmethod
    def release_order(order):
        for item in order.items.all():
            inv = ProductStoreInventory.objects.select_for_update().get(
                product=item.product,
                store_id=PACKING_STORE_ID
            )

            inv.reserved_inventory = F('reserved_inventory') - item.product_quantity
            inv.save(update_fields=['reserved_inventory'])

    @staticmethod
    def confirm_order(order):
        for item in order.items.all():
            inv = ProductStoreInventory.objects.select_for_update().get(
                product=item.product,
                store_id=PACKING_STORE_ID
            )
            previous_inventory = inv.inventory

            inv.reserved_inventory = F('reserved_inventory') - item.product_quantity
            inv.inventory = F('inventory') - item.product_quantity
            inv.save(update_fields=['reserved_inventory', 'inventory'])
            inv.refresh_from_db()

            ProductStoreInventoryHistory.objects.create(
                inventory=inv,
                action=ProductStoreInventoryHistory.DECREASE,
                quantity=item.product_quantity,
                previous_quantity=previous_inventory,
                new_quantity=inv.inventory,
                changed_by=order.customer or None
            )
