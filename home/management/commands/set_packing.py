from django.core.management import BaseCommand
from django.db import transaction as db_transaction

from server.store_configs import PACKING_STORE_ID
from store_handle.models import ProductStoreInventory
from products.models import ProductInventory
from users.models import User


class Command(BaseCommand):
    help = 'Fix and sync packing safely'

    def handle(self, *args, **options):
        with db_transaction.atomic():
            user = User.objects.get(username='soroosh')
            inventorties = ProductInventory.objects.select_for_update().all()
            for inv in inventorties:
                packing_inv, created = ProductStoreInventory.objects.select_for_update().get_or_create(
                    product=inv.product, store_id=PACKING_STORE_ID
                )
                packing_inv.handle_inventory_in_store(val=inv.inventory, user=user)
                print(packing_inv.product.name, ' done ', flush=True)
