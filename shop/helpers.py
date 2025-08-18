from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db import transaction
from django.db.models import F

from server.store_configs import PACKING_STORE_ID


def reduce_inventory(product_id, val, user=None):

    with transaction.atomic():
        from store_handle.models import ProductStoreInventory, ProductStoreInventoryHistory
        try:
            inventory = ProductStoreInventory.objects.select_for_update().get(
                product_id=product_id, store_id=PACKING_STORE_ID)
            previous_quantity = inventory.inventory
            inventory.inventory = F('inventory') - val
            inventory.save()
            inventory.refresh_from_db()

            ProductStoreInventoryHistory.objects.create(
                inventory=inventory,
                action=ProductStoreInventoryHistory.DECREASE,
                quantity=val,
                previous_quantity=previous_quantity,
                new_quantity=inventory.inventory,
                changed_by=user
            )
        except ObjectDoesNotExist:
            raise ValidationError('product inventory not found')


def increase_inventory(product_id, val, user=None):
    from store_handle.models import ProductStoreInventory, ProductStoreInventoryHistory
    with transaction.atomic():
        try:
            inventory = ProductStoreInventory.objects.select_for_update().get(
                product_id=product_id, store_id=PACKING_STORE_ID)

            previous_quantity = inventory.inventory
            inventory.inventory = F('inventory') + val
            inventory.save()
            inventory.refresh_from_db()

            ProductStoreInventoryHistory.objects.create(
                inventory=inventory,
                action=ProductStoreInventoryHistory.INCREASE,
                quantity=val,
                previous_quantity=previous_quantity,
                new_quantity=inventory.inventory,
                changed_by=user
            )
        except ObjectDoesNotExist:
            raise ValidationError('product inventory not found')
