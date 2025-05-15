import datetime

from django.core.management import BaseCommand
from django.db import transaction
from django.db.models import F
from woocommerce import API

from products.models import Brand



import requests
from django.core.files.base import ContentFile

from server.settings import WC_C_KEY, WC_C_SECRET


def save_brand_logo_from_url(brand_id, image_url):
    response = requests.get(image_url)
    if response.status_code == 200:
        brand = Brand.objects.get(id=brand_id)
        file_name = image_url.split('/')[-1]
        brand.logo.save(file_name, ContentFile(response.content), save=True)


class Command(BaseCommand):
    help = 'retrieve brands'

    def handle(self, *args, **options):
        Brand.objects.all().delete()
        wcapi = API(
            url="https://exuni.ir",
            consumer_key=WC_C_KEY,
            consumer_secret=WC_C_SECRET,
            version="wc/v3",
            wp_api=True
        )
        page = 1
        response_len = 100
        while response_len == 100:
            response = wcapi.get("products/attributes/1/terms", params={"per_page": 100, 'page': page})
            for brand in response:
                print(brand)
                print(brand['id'])
                Brand.objects.create(
                    unique_code=int(brand['id']),
                    name=brand['name'],
                    slug=brand['slug'],
                )
            page += 1

        response = wcapi.get("products/brands").json()
        for b in response:
            brand = Brand.objects.filter(slug=b['slug'])
            if brand and b['image']:
                save_brand_logo_from_url(brand_id=brand.first().id, image_url=b['image']['src'])







