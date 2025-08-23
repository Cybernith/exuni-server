from django.core.management import BaseCommand
from django.db import transaction
from django.db.models import Q, F
from datetime import datetime, timedelta

from financial_management.models import Payment
from server.store_configs import PACKING_STORE_ID
from shop.models import ShopOrder, Cart
from store_handle.models import ProductStoreInventory, ProductStoreInventoryHistory


class Command(BaseCommand):
    help = 'Cancel expired pending orders and restore inventory & cart items.'

    def handle(self, *args, **options):
        datetime_check = datetime.now() - timedelta(seconds=1)

        expired_order_ids = list(
            ShopOrder.objects.filter(
                status=ShopOrder.PENDING,
                date_time__lt=datetime_check
            ).values_list('id', flat=True)
        )

        if not expired_order_ids:
            return

        for order_id in expired_order_ids:
            self.expire_order(order_id)

    @staticmethod
    def expire_order(order_id):
        with transaction.atomic():
            order = (
                ShopOrder.objects
                .select_for_update()
                .get(id=order_id)
            )

            order.expired_order()

            cart_updates = []

            for item in order.items.all():
                cart_updates.append((item.product, item.product_quantity))

            for product, qty in cart_updates:
                cart_item, created = Cart.objects.get_or_create(
                    customer=order.customer,
                    product=product,
                    defaults={'quantity': qty}
                )
                if not created:
                    cart_item.quantity = F('quantity') + qty
                    cart_item.save(update_fields=['quantity'])

            try:
                payment = order.bank_payment
            except:
                payment = None

            if payment and payment.status in [Payment.INITIATED, Payment.PENDING]:
                payment.mark_as_expired_payment()

            order.save()

