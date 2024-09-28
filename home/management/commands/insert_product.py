
from django.core.management.base import BaseCommand

from django.core.management.base import BaseCommand

from products.models import Product, ProductProperty, Brand, Category
from server.settings import BASE_DIR
import pandas as pd



class Command(BaseCommand):
    help = 'insert moadian wares'

    def handle(self, *args, **options):
        file_path = f'{BASE_DIR}/home/management/commands/products.csv'

        data = pd.read_csv(file_path, skiprows=0).values
        for row in data:
            properties = str(row[27]).split(',')
            product_properties = []
            for prop in properties:
                if prop != 'nan':
                    if not ProductProperty.objects.filter(name=prop).exists():
                        product_prop = ProductProperty.objects.create(name=prop)
                        product_properties.append(product_prop)
                    else:
                        product_properties.append(ProductProperty.objects.filter(name=prop).first())


            brand = None
            made_in = None
            if row[39] == 'ساخت کشور':
                made_in = row[40]
            elif row[39] == 'برند':
                brand = row[40]

            if row[43] == 'ساخت کشور':
                made_in = row[44]
            elif row[43] == 'برند':
                brand = row[44]

            if not Product.objects.filter(product_id=row[2]).exists():
                if row[25] > 1:
                    price = row[25]
                else:
                    price = 0
                if row[24] > 1:
                    sale_price = row[24]
                else:
                    sale_price = 0
                if type(row[14]) == type(1):
                    first_inventory = row[14]
                else:
                    first_inventory = 0
                product = Product.objects.create(
                    product_id=row[2],
                    name=row[3],
                    summary_explanation=row[7],
                    explanation=row[8],
                    first_inventory=first_inventory,
                    price=price,
                    sale_price=sale_price,
                )

                for prop in product_properties:
                    product.properties.add(prop)

                if brand:
                    if Brand.objects.filter(name=brand).exists():
                        product_brand = Brand.objects.filter(name=brand).first()
                    else:
                        product_brand = Brand.objects.create(name=brand)
                    if made_in:
                        product_brand.made_in = made_in
                        if made_in == 'ایران':
                            is_domestic = True
                        else:
                            is_domestic = False
                        product_brand.is_domestic = is_domestic
                        product_brand.save()
                        print(product_brand.name, '   brand inserted')
                    product.brand = product_brand

                    product.save()
                print(product.name, '   product inserted')

                categories = str(row[26]).split('>')
                main_category = None
                for category in categories:
                    if category != 'nan':
                        if Category.objects.filter(name=category).exists():
                            category = Category.objects.filter(name=category).first()
                            main_category = category
                        else:
                            category = Category.objects.create(name=category)
                            if main_category:
                                category.parent = main_category
                                category.save()
                                main_category = category
                if main_category:
                    product.category = main_category
                    product.save()

                product.save()




