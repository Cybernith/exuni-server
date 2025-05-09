from django.core.management import BaseCommand
from django.db import transaction
from django.db.models import F
from woocommerce import API

from products.models import ProductProperty, ProductPropertyTerm, Brand


class Command(BaseCommand):
    help = 'retrieve properties'

    def handle(self, *args, **options):
        ProductProperty.objects.all().delete()
        wcapi = API(
            url="https://exuni.ir",
            consumer_key="ck_7df59e4d651a9449c675f453ea627481f13a4690",
            consumer_secret="cs_c1a783a3d1bbe9b3d552119fa174dc84824f5c64",
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








