from django.core.management import BaseCommand
import csv

from django.db.models import Q

from main.models import Currency
from products.models import Product, Brand, ProductPrice


class Command(BaseCommand):
    help = "Read DO and DM columns from CSV and print with row index"

    def handle(self, *args, **options):
        brands = Brand.objects.filter(name__icontains='چین')
        yoan = Currency.objects.get(id=17)
        products = Product.objects.filter(
            Q(brand_in=brands) | Q(variation_of__brand_in=brands) | Q(currency=yoan) | Q(variation_of__currency=yoan)
        )
        products = products.exclude(Q(base_price=0) | Q(base_price__isnull=True))
        products = products.exclude(Q(profit_margin=0) | Q(profit_margin__isnull=True))
        for product in products:
            price = product.base_price + (product.base_price / 100 * products.profit_margin)
            price = price * 14300
            product_price, created = ProductPrice.objects.get_or_create(product=product)
            product_price.change_price(
                val=int(price),
                note=f"Applied 14,300 rate yoan"
            )
            product.update(price=price, regular_price=price)




