from dataclasses import dataclass
from typing import List, Tuple, Dict
from django.db import transaction
from django.db.models import F
from django.utils.timezone import now

from products.models import Product
from server.store_configs import PACKING_STORE_ID
from shop.models import ShopOrder, ShopOrderItem
from store_handle.models import ProductStoreInventory, ProductStoreInventoryHistory


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
    ) -> Tuple[ShopOrder or None, List[Dict]]:

        shop_order = ShopOrder.objects.create(
            customer=customer,
            date_time=now(),
            shipment_address=address,
            discount_code=discount_code,
        )

        product_ids = [cart.product_id for cart in cart_lines]
        products = (
            Product.objects.filter(pk__in=product_ids).prefetch_related("store_inventory")
        )

        product_map = {p.id: p for p in products}

        if all(
                (p := product_map.get(line.product_id)) is None or p.available_inventory <= 0
                for line in cart_lines
        ):
            return None, [{
                "message": "هیچ موجودی برای محصولات سبد خرید وجود ندارد"
            }]

        order_items_to_create: List[ShopOrderItem] = []
        shortages: List[Dict] = []

        order_items_to_create: List[ShopOrderItem] = []
        shortages: List[Dict] = []

        for line in cart_lines:
            product = product_map.get(line.product_id)
            if not product:
                shortages.append({
                    "product_id": line.product_id,
                    "requested": line.quantity,
                    "processed": 0,
                    "leftover": line.quantity,
                    "name": f"#{line.product_id}",
                })
                continue

            available = product.available_inventory
            if available <= 0:
                shortages.append({
                    'product_id': line.product_id, 'requested': line.quantity,
                    'processed': 0, 'leftover': line.quantity, 'name': product.name
                })
                continue

            to_process = min(line.quantity, available)

            if to_process > 0:
                order_items_to_create.append(
                    ShopOrderItem(
                        shop_order=shop_order,
                        product=product,
                        price=line.price,
                        product_quantity=to_process
                    )
                )
                packing_inventory, created = ProductStoreInventory.objects.select_for_update().get_or_create(
                    product=product,
                    store_id=PACKING_STORE_ID,
                    defaults={'inventory': 0}
                )
                previous_quantity = packing_inventory.inventory
                packing_inventory.inventory = F('inventory') - to_process
                packing_inventory.save()
                packing_inventory.refresh_from_db(fields=['inventory'])

                ProductStoreInventoryHistory.objects.create(
                    inventory=packing_inventory,
                    action=ProductStoreInventoryHistory.DECREASE,
                    quantity=to_process,
                    previous_quantity=previous_quantity,
                    new_quantity=previous_quantity - to_process,
                    changed_by=customer
                )

            if to_process < line.quantity:
                shortages.append({
                    'product_id': line.product_id,
                    'requested': line.quantity,
                    'processed': to_process,
                    'leftover': line.quantity - to_process,
                    'name': product.name
                })

        if order_items_to_create:
            ShopOrderItem.objects.bulk_create(order_items_to_create)

        inventory_info = 'ok'
        if shortages:
            parts = [f'{s["name"]}: پردازش‌شده {s["processed"]} از {s["requested"]}'
                     for s in shortages]
            inventory_info = (
                    'موجودی برخی اقلام کمتر از مقدار درخواستی بود. '
                    + ' ؛ '.join(parts)
                    + ' . سبد بر اساس موجودی فعلی ثبت شد.'
            )

        shop_order.update(inventory_info=inventory_info)
        shop_order.set_constants()

        return shop_order, shortages
