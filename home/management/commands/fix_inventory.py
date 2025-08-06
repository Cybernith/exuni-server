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

            for packing in packing_inventories:
                product = packing.product
                inventory = ProductInventory.objects.get(product=product)
                inventory.handle_inventory(packing.inventory, user=None)
                print(product.name, ' >> inventory changed to = ', packing.inventory, flush=True)

            orders_must_reduce = ShopOrder.objects.filter(
                Q(id__gte=4167) & Q(status__in=[ShopOrder.PENDING, ShopOrder.PROCESSING, ShopOrder.PAID])
            ).prefetch_related('items')
            for order in orders_must_reduce:
                for item in order.items.all():
                    reduce_inventory(item.product.id, item.product_quantity)
                    print(' reduced', flush=True)

