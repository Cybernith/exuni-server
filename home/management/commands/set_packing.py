from django.core.management import BaseCommand
from django.db import transaction as db_transaction

from store_handle.models import  ProductStoreInventoryHandle


class Command(BaseCommand):
    help = 'Fix and sync packing safely'

    def handle(self, *args, **options):
        with db_transaction.atomic():
            handles = ProductStoreInventoryHandle.objects.exclude(store_id=1)
            for handle in handles:
                handle.apply()
                print('applied')

