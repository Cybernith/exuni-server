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


class Command(BaseCommand):
    help = 'fetch products data'

    def handle(self, *args, **options):
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
                if product['type'] == 'variable':
                    product['variations'] = wcapi.get(f"products/{product['id']}/variations",
                                                      params={"per_page": 50, 'page': 1}).json()
                file_name = 'products.json'
                with open(file_name, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                data.append(product)
                with open(file_name, 'w', encoding='utf-8') as file:
                    json.dump(data, file, ensure_ascii=False, indent=4)

            print(f'{20 * page} product retrieved')
            page += 1
            response_len = len(products)








