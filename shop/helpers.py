from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db import transaction
from django.db.models import F

from products.models import ProductInventoryHistory, ProductInventory


def reduce_inventory(product_id, val, user=None):

    with transaction.atomic():
        try:
            inventory = ProductInventory.objects.select_for_update().get(product_id=product_id)

            if inventory.inventory < val:
                raise ValidationError('موجودی کالا کافی نیست')

            previous_quantity = inventory.inventory
            inventory.inventory = F('inventory') - val
            inventory.save()
            inventory.refresh_from_db()

            ProductInventoryHistory.objects.create(
                inventory=inventory,
                action=ProductInventoryHistory.DECREASE,
                amount=val,
                previous_quantity=previous_quantity,
                new_quantity=inventory.inventory,
                changed_by=user
            )
        except ObjectDoesNotExist:
            raise ValidationError('product inventory not found')


def increase_inventory(product_id, val, user=None):

    with transaction.atomic():
        try:
            inventory = ProductInventory.objects.select_for_update().get(product_id=product_id)

            previous_quantity = inventory.inventory
            inventory.inventory = F('inventory') + val
            inventory.save()
            inventory.refresh_from_db()

            ProductInventoryHistory.objects.create(
                inventory=inventory,
                action=ProductInventoryHistory.INCREASE,
                amount=val,
                previous_quantity=previous_quantity,
                new_quantity=inventory.inventory,
                changed_by=user
            )
        except ObjectDoesNotExist:
            raise ValidationError('product inventory not found')
