from django.core.management import BaseCommand

from financial_management.models import Payment
from shop.models import ShopOrder


class Command(BaseCommand):
    help = 'change status'

    def handle(self, *args, **options):
        orders = ShopOrder.objects.filter(status=ShopOrder.PAID)
        for order in orders:
            try:
                if order.bank_payment and order.bank_payment.status == Payment.SUCCESS:
                    order.update(status=ShopOrder.PROCESSING)
            except:
                pass

