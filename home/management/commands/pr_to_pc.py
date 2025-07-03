from django.core.management import BaseCommand

from shop.models import ShopOrder


class Command(BaseCommand):
    help = 'change status'

    def handle(self, *args, **options):
        ShopOrder.objects.filter(status=ShopOrder.PROCESSING).update(status=ShopOrder.PACKED)
