from dataclasses import dataclass
from typing import List, Tuple, Dict
from django.db import transaction
from django.db.models import F
from django.utils.timezone import now

from products.models import ProductInventory, ProductInventoryHistory
from shop.models import ShopOrder, ShopOrderItem


@dataclass(frozen=True)
class CartLine:
    product_id: int
    quantity: int
    price: int


class InventoryAllocatorService:

    @staticmethod
    @transaction.atomic
    def create_order_and_allocate(
            customer,
            address,
            cart_lines: List[CartLine],
            discount_code=None
    ) -> Tuple[ShopOrder, List[Dict]]:

        shop_order = ShopOrder.objects.create(
            customer=customer,
            date_time=now(),
            shipment_address=address,
            discount_code=discount_code,
        )

        product_ids = [cart.product_id for cart in cart_lines]
        inventories = (
            ProductInventory.objects.filter(product_id__in=product_ids).select_related('product').select_for_update()
        )

        inventories_map = {inventory.product_id: inventory for inventory in inventories}

        if all((product_inventory := inventories_map.get(line.product_id)) is None or product_inventory.inventory <= 0
               for line in cart_lines):
            return None, [{
                'message': 'هیچ موجودی برای محصولات سبد خرید وجود ندارد'
            }]


        order_items_to_create: List[ShopOrderItem] = []
        shortages: List[Dict] = []

        order_items_to_create: List[ShopOrderItem] = []
        shortages: List[Dict] = []

        for line in cart_lines:
            inv = inventories_map.get(line.product_id)
            if not inv:
                shortages.append({
                    'product_id': line.product_id, 'requested': line.quantity,
                    'processed': 0, 'leftover': line.quantity, 'name': f'#{line.product_id}'
                })
                continue

            available = inv.inventory
            if available <= 0:
                shortages.append({
                    'product_id': line.product_id, 'requested': line.quantity,
                    'processed': 0, 'leftover': line.quantity, 'name': inv.product.name
                })
                continue

            to_process = min(line.quantity, available)

            if to_process > 0:
                order_items_to_create.append(
                    ShopOrderItem(
                        shop_order=shop_order,
                        product=inv.product,
                        price=line.price,
                        product_quantity=to_process
                    )
                )

                prev_qty = inv.inventory
                ProductInventory.objects.filter(pk=inv.pk).update(
                    inventory=F('inventory') - to_process
                )
                inv.refresh_from_db(fields=['inventory'])

                ProductInventoryHistory.objects.create(
                    inventory=inv,
                    action=ProductInventoryHistory.DECREASE,
                    amount=to_process,
                    previous_quantity=prev_qty,
                    new_quantity=prev_qty - to_process,
                    changed_by=customer
                )

            if to_process < line.quantity:
                shortages.append({
                    'product_id': line.product_id,
                    'requested': line.quantity,
                    'processed': to_process,
                    'leftover': line.quantity - to_process,
                    'name': inv.product.name
                })

        if order_items_to_create:
            ShopOrderItem.objects.bulk_create(order_items_to_create)

        shop_order.set_constants()

        return shop_order, shortages
