from django.core.management import BaseCommand
from django.db import transaction
from django.db.models import Q, F
from datetime import datetime, timedelta

from financial_management.models import Payment
from shop.models import ShopOrder, Cart
from products.models import ProductInventory, ProductInventoryHistory


class Command(BaseCommand):
    help = 'Cancel expired pending orders and restore inventory & cart items.'

    def handle(self, *args, **options):
        #datetime_check = datetime.now() - timedelta(hours=5)

        expired_order_ids = list(
            ShopOrder.objects.filter(
                status=ShopOrder.PENDING,
            ).values_list('id', flat=True)
        )

        if not expired_order_ids:
            return

        for order_id in expired_order_ids:
            self.expire_order(order_id)

    def expire_order(self, order_id):
        with transaction.atomic():
            order = (
                ShopOrder.objects
                .select_related('customer')
                .prefetch_related('items__product__current_inventory')
                .select_for_update()
                .get(id=order_id)
            )

            order.expired_order()

            inventory_updates = []
            cart_updates = []

            for item in order.items.all():
                inventory_updates.append((item.product.id, item.product_quantity))
                cart_updates.append((item.product, item.product_quantity))

            for product_id, qty in inventory_updates:
                self._increase_inventory(product_id, qty, user=None)

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

    @staticmethod
    def _increase_inventory(product_id, val, user=None):
        inventory = (
            ProductInventory.objects
            .select_for_update()
            .get(product_id=product_id)
        )

        previous_quantity = inventory.inventory
        inventory.inventory = F('inventory') + val
        inventory.save(update_fields=['inventory'])
        inventory.refresh_from_db()

        ProductInventoryHistory.objects.create(
            inventory=inventory,
            action=ProductInventoryHistory.INCREASE,
            amount=val,
            previous_quantity=previous_quantity,
            new_quantity=inventory.inventory,
            changed_by=user
        )
