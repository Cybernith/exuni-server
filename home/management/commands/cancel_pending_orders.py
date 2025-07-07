from django.core.management import BaseCommand

from shop.models import ShopOrder


class Command(BaseCommand):
    help = 'cancel pending orders'

    def handle(self, *args, **options):
        shop_orders = ShopOrder.objects.filter(status=ShopOrder.PENDING)
        for order in shop_orders:
            order.cancel_order()
