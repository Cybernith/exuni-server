from django.core.management import BaseCommand
from django.db import transaction
from django.db.models import F
from woocommerce import API

from products.models import Category
from server.settings import WC_C_KEY, WC_C_SECRET


class Command(BaseCommand):
    help = 'retrieve categories'

    def handle(self, *args, **options):
        Category.objects.all().delete()
        wcapi = API(
            url="https://exuni.ir",
            consumer_key=WC_C_KEY,
            consumer_secret=WC_C_SECRET,
            version="wc/v3",
            wp_api=True
        )
        category_list = []
        for page in [1, 2]:
            response = wcapi.get("products/categories", params={"per_page": 100, 'page': page}).json()
            for cat in response:
                len(cat['name'])
                print(cat['id'])
                category_list.append(
                    {
                        'slug': cat['slug'],
                        'name': cat['name'],
                        'unique_code': cat['id'],
                        'parent_unique_code': cat['parent'],
                    }
                )

        with transaction.atomic():
            categories = [Category(**item) for item in category_list]
            Category.objects.bulk_create(categories)
            for category in Category.objects.exclude(parent_unique_code=0):
                category.update(parent=Category.objects.get(unique_code=category.parent_unique_code))





