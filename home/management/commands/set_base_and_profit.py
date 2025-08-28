from django.core.management import BaseCommand
import csv

from products.models import Product


class Command(BaseCommand):
    help = "Read DO and DM columns from CSV and print with row index"

    def handle(self, *args, **options):
        with open("test.csv", "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader)  # Skip header row
            products = Product.objects.all()

            for row_idx, row in enumerate(reader, start=2):  # row 2 = first data row
                try:
                    price = row[116]
                except IndexError:
                    price = None
                try:
                    profit = row[118]
                except IndexError:
                    profit = None
                try:
                    sku = row[2]
                except IndexError:
                    sku = None
                try:
                    product_id = row[0]
                except IndexError:
                    product_id = None

                if (profit or profit == '0') and (profit != '' or profit != ' '):
                    profit = round(float(profit))
                else:
                    profit = None

                if (price or price == '0') and (price != '' or price != ' '):
                    price = float(price)
                else:
                    price = None

                find_product = False

                if product_id:
                    product = products.filter(product_id=product_id.strip())
                    if product.exists():
                        product.first().update(base_price=price, profit_margin=profit)
                        find_product = True
                        print(product.first().name,product.first().id, f' fixed >> base : {price}  profit : {profit}')

                if sku and not find_product:
                    product = products.filter(sixteen_digit_code=sku.strip())
                    if product.exists():
                        product.first().update(base_price=price, profit_margin=profit)
                        print(product.first().name, product.first().id, f' fixed >> base : {price}  profit : {profit}')

                if not find_product:
                    print(f' sku {sku or " - "} not found')







