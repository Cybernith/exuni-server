from django.core.management import BaseCommand
from django.db import transaction as db_transaction
from django.db.models import Q, F

from shop.models import ShopOrder
from store_handle.models import ProductStoreInventory
from products.models import ProductInventoryHistory, ProductInventory


class Command(BaseCommand):
    help = 'Fix and sync inventory safely'

    def handle(self, *args, **options):
        with db_transaction.atomic():
            ProductInventory.objects.all().update(inventory=0)

            packing_inventories = ProductStoreInventory.objects.select_related('product').filter(store_id=1)
            product_ids = [p.product.id for p in packing_inventories]
            inventory_map = {
                inv.product_id: inv
                for inv in ProductInventory.objects.select_for_update().filter(product_id__in=product_ids)
            }

            for packing in packing_inventories:
                inv = inventory_map[packing.product.id]
                previous_quantity = inv.inventory
                inv.inventory = packing.inventory
                inv.save()
                ProductInventoryHistory.objects.create(
                    inventory=inv,
                    action=ProductInventoryHistory.STORE_HANDLE,
                    amount=packing.inventory,
                    previous_quantity=previous_quantity,
                    new_quantity=inv.inventory,
                    changed_by=None
                )
                print(f'{packing.product.name} >> inventory set to {packing.inventory}', flush=True)

            orders_must_reduce = ShopOrder.objects.filter(
                Q(date_time__gte=ShopOrder.objects.get(id=6691).date_time,
                  status__in=[ShopOrder.PROCESSING, ShopOrder.PAID, ShopOrder.SHIPPED]) |
                Q(id__in=[878, 4167])
            ).prefetch_related('items__product')

            for order in orders_must_reduce:
                with db_transaction.atomic():
                    for item in order.items.all():
                        inventory = ProductInventory.objects.select_for_update().get(product_id=item.product.id)
                        val = min(inventory.inventory, item.product_quantity)
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
                            changed_by=None
                        )
                        print(f'{item.product.name} >> reduced val: {val}, remaining {inventory.inventory}', flush=True)
