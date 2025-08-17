from django.db import transaction
from products.models import ProductInventory, ProductInventoryHistory
from django.db.models import F


class PayExpiredOrderService:

    @staticmethod
    @transaction.atomic
    def reserve_inventory(order, user=None):
        items = list(order.items.select_related("product__current_inventory"))
        product_ids = [item.product_id for item in items]

        inventories = {
            inv.product_id: inv
            for inv in ProductInventory.objects.select_for_update().filter(product_id__in=product_ids)
        }

        for item in items:
            product_inventory = inventories[item.product_id]

            if product_inventory.inventory < item.product_quantity:
                item.update(product_quantity=product_inventory.inventory)

            if item.product_quantity <= 0:
                item.delete()
                continue

            previous_quantity = product_inventory.inventory
            product_inventory.inventory = F("inventory") - item.product_quantity
            product_inventory.save(update_fields=["inventory"])
            product_inventory.refresh_from_db()

            ProductInventoryHistory.objects.create(
                inventory=product_inventory,
                action=ProductInventoryHistory.DECREASE,
                amount=item.product_quantity,
                previous_quantity=previous_quantity,
                new_quantity=product_inventory.inventory,
                changed_by=user
            )
