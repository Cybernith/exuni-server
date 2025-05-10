from django.core.management import BaseCommand
from django.db import transaction
from django.db.models import F
from woocommerce import API

from main.models import Currency
from products.models import Product, ProductGallery, Category, Brand, ProductProperty, ProductAttribute, \
    ProductAttributeTerm, ProductPropertyTerm
from users.models import User
import json
import requests
from django.core.files.base import ContentFile


def save_product_picture_from_url(product_id, image_url):
    response = requests.get(image_url)
    if response.status_code == 200:
        current_product = Product.objects.get(id=product_id)
        file_name = image_url.split('/')[-1]
        current_product.picture.save(file_name, ContentFile(response.content), save=True)
        # print(f'picture added to {current_product.name}')
        return current_product.picture


def add_product_picture_gallery_from_url(product_id, image_urls):
    for image_url in image_urls:
        response = requests.get(image_url)
        # counter = 1
        if response.status_code == 200:
            product = Product.objects.get(id=product_id)
            gallery = ProductGallery.objects.create(product=product)
            file_name = image_url.split('/')[-1]
            gallery.picture.save(file_name, ContentFile(response.content), save=True)
            # print(f'{counter} picture added to {product.name} gallery')
            # counter += 1

class Command(BaseCommand):
    help = 'retrieve properties'

    def handle(self, *args, **options):
        Product.objects.filter(product_type=Product.VARIATION).delete()
        Product.objects.all().delete()
        wcapi = API(
            url="https://exuni.ir",
            consumer_key="ck_7df59e4d651a9449c675f453ea627481f13a4690",
            consumer_secret="cs_c1a783a3d1bbe9b3d552119fa174dc84824f5c64",
            version="wc/v3",
            wp_api=True,
            timeout=120
        )
        page = 1
        response_len = 20
        while response_len == 20:
            products = wcapi.get("products", params={"per_page": 20, 'page': page}).json()
            for product in products:
                if product['type'] == 'simple':
                    new_product = Product.objects.create(
                        product_type=Product.SIMPLE,
                        product_id=product['id'],
                        slug=product['slug'],
                        status=product['status'],
                        sixteen_digit_code=product['sku'],
                        name=product['name'],
                        regular_price=float(product['regular_price']) if product['regular_price'] else None,
                        price=float(product['price']) if product['price'] else None,
                        sale_price=float(product['sale_price']) if product['sale_price'] else None,
                        explanation=product['description'],
                        summary_explanation=product['short_description'],
                        first_inventory=int(product['stock_quantity']) if product['stock_quantity'] else None,
                    )
                    for category in product['categories']:
                        new_product.category.add(Category.objects.get(unique_code=category['id']))
                    pictures = product['images']
                    if len(pictures) > 1:
                        pic = save_product_picture_from_url(new_product.id, pictures[0]['src'])
                        new_product.picture = pic
                        add_product_picture_gallery_from_url(new_product.id, [item['src'] for item in pictures[1:]])
                    else:
                        pic = save_product_picture_from_url(new_product.id, pictures[0]['src'])
                        new_product.picture = pic

                    attributes = product['attributes']
                    meta_datas = product['meta_data']

                    product_attributes = [item for item in attributes if item["id"] not in [0, 1, 2]]

                    brand_name = next((attribute for attribute in attributes if attribute["id"] == 1), None)

                    made_in = next((attribute for attribute in attributes if attribute["id"] == 2), None)

                    currency = next((meta_data for meta_data in meta_datas if
                                     meta_data["key"] == "_mnswmc_currency_ids"), None)

                    profit_margin = next((meta_data for meta_data in meta_datas if
                                          meta_data["key"] == "_mnswmc_profit_margin"), None)

                    currency_price = next((meta_data for meta_data in meta_datas if
                                          meta_data["key"] == "_mnswmc_regular_price"), None)
                    if currency and currency['value'] != '[]':
                        currency_code = currency['value'].translate({ord(i): None for i in '[]'})
                        new_product.currency = Currency.objects.get(unique_code=int(currency_code))

                    if brand_name and brand_name['options'][0]:
                        new_product_brand = Brand.objects.get(name=brand_name['options'][0])
                        new_product.brand = new_product_brand
                        new_product_brand.made_in = made_in['options'][0]

                    if profit_margin:
                        new_product.profit_margin = float(profit_margin['value']) if profit_margin['value'] else None
                    if currency_price:
                        new_product.currency_price = float(currency_price['value']) if currency_price['value'] else None
                    new_product.save()

                    for product_attribute in product_attributes:
                        product_property = ProductProperty.objects.get(unique_code=product_attribute['id'])
                        new_product_attribute = ProductAttribute.objects.create(
                            product=new_product,
                            product_property=product_property
                        )
                        new_product_attribute_term = ProductAttributeTerm.objects.create(
                            product_attribute=new_product_attribute
                        )
                        for term in product_attribute['options']:
                            new_product_attribute_term.terms.add(
                                ProductPropertyTerm.objects.get(name=term)
                            )

                elif product['type'] == 'variable':
                    new_product = Product.objects.create(
                        product_type=Product.VARIABLE,
                        product_id=product['id'],
                        slug=product['slug'],
                        status=product['status'],
                        sixteen_digit_code=product['sku'],
                        name=product['name'],
                        regular_price=float(product['regular_price']) if product['regular_price'] else 0,
                        price=float(product['price']) if product['price'] else 0,
                        sale_price=float(product['sale_price']) if product['sale_price'] else 0,
                        explanation=product['description'],
                        summary_explanation=product['short_description'],
                        first_inventory=int(product['stock_quantity']) if product['stock_quantity'] else 0,
                    )
                    for category in product['categories']:
                        new_product.category.add(Category.objects.get(unique_code=category['id']))
                    pictures = product['images']
                    if len(pictures) > 1:
                        pic = save_product_picture_from_url(new_product.id, pictures[0]['src'])
                        new_product.picture = pic
                        add_product_picture_gallery_from_url(new_product.id, [item['src'] for item in pictures[1:]])
                    else:
                        pic = save_product_picture_from_url(new_product.id, pictures[0]['src'])
                        new_product.picture = pic

                    attributes = product['attributes']
                    meta_datas = product['meta_data']

                    product_attributes = [item for item in attributes if item["id"] not in [0, 1, 2]]

                    brand_name = next((attribute for attribute in attributes if attribute["name"] == "برند"), None)

                    variation_title = next((attribute['name'] for attribute in attributes if attribute["id"] == 0), None)
                    new_product.variation_title = variation_title

                    made_in = next((attribute for attribute in attributes if attribute["name"] == "ساخت کشور"), None)

                    currency = next((meta_data for meta_data in meta_datas if
                                     meta_data["key"] == "_mnswmc_currency_ids"), None)

                    profit_margin = next((meta_data for meta_data in meta_datas if
                                          meta_data["key"] == "_mnswmc_profit_margin"), 0)
                    currency_price = next((meta_data for meta_data in meta_datas if
                                          meta_data["key"] == "_mnswmc_regular_price"), 0)

                    if currency and currency['value'] != '[]':
                        currency_code = currency['value'].translate({ord(i): None for i in '[]'})
                        new_product.currency = Currency.objects.get(unique_code=int(currency_code))

                    if brand_name and brand_name['options'][0]:
                        new_product_brand = Brand.objects.get(name=brand_name['options'][0])
                        new_product.brand = new_product_brand
                        new_product_brand.made_in = made_in['options'][0]
                        new_product_brand.save()

                    new_product.profit_margin = float(profit_margin['value']) if profit_margin else 0
                    new_product.currency_price = float(currency_price['value']) if currency_price else 0
                    new_product.save()

                    for product_attribute in product_attributes:
                        product_property = ProductProperty.objects.get(unique_code=product_attribute['id'])
                        new_product_attribute = ProductAttribute.objects.create(
                            product=new_product,
                            product_property=product_property
                        )
                        new_product_attribute_term = ProductAttributeTerm.objects.create(
                            product_attribute=new_product_attribute
                        )
                        for term in product_attribute['options']:
                            new_product_attribute_term.terms.add(
                                ProductPropertyTerm.objects.get(name=term)
                            )

                    variations = wcapi.get(f"products/{product['id']}/variations",
                                           params={"per_page": 50, 'page': 1}).json()
                    for variation in variations:
                        new_variation = Product.objects.create(
                                variation_of=new_product,
                                variation_title=new_product.variation_title,
                                product_type=Product.VARIATION,
                                product_id=variation['id'],
                                status=variation['status'],
                                sixteen_digit_code=variation['sku'],
                                name=variation['name'],
                                regular_price=float(variation['regular_price']) if variation['regular_price'] else None,
                                price=float(variation['price']) if variation['price'] else None,
                                sale_price=float(variation['sale_price']) if variation['sale_price'] else None,
                                first_inventory=int(variation['stock_quantity']) if variation['stock_quantity'] else None,
                        )
                        pic = save_product_picture_from_url(new_variation.id, variation['image']['src'])
                        new_variation.picture = pic

                        meta_datas = variation['meta_data']

                        currency = next((meta_data for meta_data in meta_datas if
                                         meta_data["key"] == "_mnswmc_currency_id"), None)

                        profit_margin = next((meta_data for meta_data in meta_datas if
                                              meta_data["key"] == "_mnswmc_profit_margin"), None)
                        currency_price = next((meta_data for meta_data in meta_datas if
                                               meta_data["key"] == "_mnswmc_regular_price"), None)
                        if currency and currency['value'] != '':
                            currency_code = currency['value'].translate({ord(i): None for i in '[]'})
                            new_variation.currency = Currency.objects.get(unique_code=int(currency_code))

                        if profit_margin:
                            new_variation.profit_margin = float(profit_margin['value']) if profit_margin['value'] else 0
                        if currency_price:
                            new_variation.currency_price = float(currency_price['value']) if currency_price['value'] else 0
                        new_variation.save()

                        #attributes = variation['attributes']
                        #product_attributes = [item for item in attributes if item["id"] not in [0, 1, 2]]

                        # for product_attribute in product_attributes:
                        #     product_property = ProductProperty.objects.get(unique_code=product_attribute['id'])
                        #     new_product_attribute = ProductAttribute.objects.create(
                        #         product=new_variation,
                        #         product_property=product_property
                        #     )
                        #     new_product_attribute_term = ProductAttributeTerm.objects.create(
                        #         product_attribute=new_product_attribute
                        #     )
                        #     for term in product_attribute['options']:
                        #         new_product_attribute_term.terms.add(
                        #             ProductPropertyTerm.objects.get(name=term)
                        #         )

            print(f'{20 * page} product retrieved')
            page += 1
            response_len = len(products)





