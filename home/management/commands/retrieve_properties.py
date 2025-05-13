from django.core.management import BaseCommand
from django.db import transaction
from django.db.models import F
from woocommerce import API

from products.models import ProductProperty, ProductPropertyTerm, Brand
from server.settings import WC_C_KEY, WC_C_SECRET


class Command(BaseCommand):
    help = 'retrieve properties'

    def handle(self, *args, **options):
        ProductProperty.objects.all().delete()
        wcapi = API(
            url="https://exuni.ir",
            consumer_key=WC_C_KEY,
            consumer_secret=WC_C_SECRET,
            version="wc/v3",
            wp_api=True
        )
        response = wcapi.get("products/attributes", params={"per_page": 100, 'page': 1}).json()
        for prop in response:
            if not prop['id'] in [1, 2]:
                product_prop = ProductProperty.objects.create(
                    unique_code=prop['id'],
                    name=prop['name'],
                    slug=prop['slug'],
                )
                page = 1
                response_len = 100
                while response_len == 100:
                    terms = wcapi.get(f"products/attributes/{prop['id']}/terms", params={"per_page": 100, 'page': page}).json()
                    for term in terms:
                        ProductPropertyTerm.objects.create(
                            product_property=product_prop,
                            unique_code=term['id'],
                            name=term['name'],
                            slug=term['slug'],
                        )
                    page += 1
                    response_len = len(terms)








