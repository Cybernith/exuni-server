from typing import List
from shop.models import Cart, ShipmentAddress
from shop.services.inventory_allocate_service import CartLine, InventoryAllocatorService
from subscription.models import DiscountCode


class OrderAppService:

    @staticmethod
    def place_order_without_reserve(customer, address_id, discount_code_value=None):
        address = ShipmentAddress.objects.get(id=address_id, customer=customer)

        discount_code = None
        if discount_code_value:
            discount_code = DiscountCode.objects.get(code=discount_code_value)
            discount_code.verify()

        cart_qs = Cart.objects.filter(customer=customer).select_related('product')
        if not cart_qs.exists():
            raise ValueError('سبد خرید شما خالی است')

        lines: List[CartLine] = [
            CartLine(
                product_id=item.product_id,
                quantity=item.quantity,
                price=item.product.price
            ) for item in cart_qs
        ]

        shop_order, shortages = InventoryAllocatorService.create_order_and_allocate(
            customer=customer,
            address=address,
            cart_lines=lines,
            discount_code=discount_code
        )

        cart_qs.delete()

        return shop_order, shortages
