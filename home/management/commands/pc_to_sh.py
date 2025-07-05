from django.core.management import BaseCommand

from shop.models import ShopOrder


class Command(BaseCommand):
    help = 'change status'

    def handle(self, *args, **options):
        ShopOrder.objects.filter(status=ShopOrder.PACKED).update(status=ShopOrder.SHIPPED)
