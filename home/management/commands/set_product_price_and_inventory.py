from django.core.management.base import BaseCommand

from main.models import Currency
from products.models import Product, ProductInventory


class Command(BaseCommand):
    help = 'insert moadian wares'

    def handle(self, *args, **options):
        products = Product.objects.all()
        for product in products:
            if ProductInventory.objects.filter(product=product).exists():
                product_inventory = ProductInventory.objects.get(product=product)
                product_inventory.set_product_inventory()
                product_inventory.set_product_price()
                print('موجودی کالا {} تغییر کرد'.format(product.name))
            else:
                product_inventory = ProductInventory.objects.create(product=product)
                product_inventory.set_product_inventory()
                product_inventory.set_product_price()
                print('موجودی کالا {} ساخته شد'.format(product.name))






