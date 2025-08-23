from django.core.management import BaseCommand
from django.db import transaction
from django.db.models import F, Sum
from server.store_configs import PACKING_STORE_ID
from shop.models import ShopOrder
from store_handle.models import ProductStoreInventory


class Command(BaseCommand):
    help = "Fix reserved_inventory for all PENDING orders safely"

    BATCH_SIZE = 500

    def handle(self, *args, **options):
        with transaction.atomic():
            orders = ShopOrder.objects.filter(status=ShopOrder.PENDING)
            for order in orders:
                for item in order.items.all():
                    with transaction.atomic():
                        inv = ProductStoreInventory.objects.select_for_update().get(
                            store_id=PACKING_STORE_ID,
                            product=item.product
                        )
                        inv.reserved_inventory = F('reserved_inventory') + item.product_quantity
                        inv.inventory = F('inventory') + item.product_quantity
                        inv.save(update_fields=['reserved_inventory', 'inventory'])
