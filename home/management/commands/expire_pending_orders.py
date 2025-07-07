from django.core.management import BaseCommand
from django.db.models import Q

from helpers.functions import datetime_to_str
from shop.models import ShopOrder
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'cancel pending orders'

    def handle(self, *args, **options):
        print(f'cron job run in {datetime_to_str(datetime.now())}')
        datetime_check = datetime.now() - timedelta(hours=5)
        shop_orders = ShopOrder.objects.filter(Q(status=ShopOrder.PENDING) & Q(date_time__lt=datetime_check))
        for order in shop_orders:
            order.expired_order()
