from django.core.management import BaseCommand
from django.db import transaction
from django.db.models import F
from woocommerce import API

from products.models import Product, ProductGallery
from users.models import User
import json
import requests
from django.core.files.base import ContentFile


def save_product_picture_from_url(product_id, image_url):
    response = requests.get(image_url)
    if response.status_code == 200:
        product = Product.objects.get(id=product_id)
        file_name = image_url.split('/')[-1]
        product.picture.save(file_name, ContentFile(response.content), save=True)
        print(f'picture added to {product.name}')


def add_product_picture_gallery_from_url(product_id, image_urls):
    for image_url in image_urls:
        response = requests.get(image_url)
        counter = 1
        if response.status_code == 200:
            product = Product.objects.get(id=product_id).only('id', 'name')
            gallery = ProductGallery.objects.create(product=product)
            file_name = image_url.split('/')[-1]
            gallery.picture.save(file_name, ContentFile(response.content), save=True)
            print(f'{counter} picture added to {product.name} gallery')
            counter += 1

class Command(BaseCommand):
    help = 'retrieve properties'

    def handle(self, *args, **options):
        Product.objects.all().delete()
        wcapi = API(
            url="https://exuni.ir",
            consumer_key="ck_7df59e4d651a9449c675f453ea627481f13a4690",
            consumer_secret="cs_c1a783a3d1bbe9b3d552119fa174dc84824f5c64",
            version="wc/v3",
            wp_api=True
        )
        page = 1
        response_len = 20
        while response_len == 20:
            products = wcapi.get("products", params={"per_page": 20, 'page': page}).json()
            for product in products:
                Product.objects.create(
                    product_type=product['status'],
                    product_id=product['id'],
                    slug=product['slug'],
                    sixteen_digit_code=product['sku'],
                    name=product['name'],
                    explanation=product['description'],
                    summary_explanation=product['short_description'],
                )

            print(f'{20 * page} product retrieved')
            page += 1
            response_len = len(products)

            # users = [User(**item) for item in users_list]
            # User.objects.bulk_create(users)





