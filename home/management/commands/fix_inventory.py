from django.core.management import BaseCommand
from django.db import transaction as db_transaction
from django.db.models import Q, Prefetch

from products.models import ProductInventory, ProductInventoryHistory
from shop.helpers import reduce_inventory
from shop.models import ShopOrder, ShopOrderItem
from store_handle.models import ProductStoreInventory


class Command(BaseCommand):
    help = 'fix inventory'

    def handle(self, *args, **options):
        with db_transaction.atomic():
            ProductInventory.objects.all().update(inventory=0)
            packing_inventories = ProductStoreInventory.objects.select_related('product').filter(store_id=1)
            product_inventories = {
                inv.product_id: inv for inv in ProductInventory.objects.select_related('product').all()
            }

            updated_inventories = []
            history_logs = []

            for packing in packing_inventories:
                product = packing.product
                inventory_obj = product_inventories.get(product.id)
                if not inventory_obj:
                    continue

                previous_quantity = inventory_obj.inventory
                new_quantity = packing.inventory

                inventory_obj.inventory = new_quantity
                updated_inventories.append(inventory_obj)

                history_logs.append(ProductInventoryHistory(
                    inventory=inventory_obj,
                    action=ProductInventoryHistory.STORE_HANDLE,
                    amount=new_quantity,
                    previous_quantity=previous_quantity,
                    new_quantity=new_quantity,
                    changed_by=None
                ))

                print(product.name, ' >> inventory changed to = ', new_quantity, flush=True)

            ProductInventory.objects.bulk_update(updated_inventories, ['inventory'])
            ProductInventoryHistory.objects.bulk_create(history_logs)

            print('sync inventories', flush=True
                  )
            orders_must_reduce = ShopOrder.objects.filter(
                Q(id__gte=4167) | Q(status=ShopOrder.PENDING)).prefetch_related(
                Prefetch('items', queryset=ShopOrderItem.objects.select_related('product'))
            )
            for order in orders_must_reduce:
                for item in order.items.all():
                    reduce_inventory(item.product.id, item.product_quantity)
