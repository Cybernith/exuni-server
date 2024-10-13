
from django.core.management.base import BaseCommand

from django.core.management.base import BaseCommand

from main.models import Currency
from products.models import Product, ProductProperty, Brand, Category
from server.settings import BASE_DIR
import pandas as pd



class Command(BaseCommand):
    help = 'insert moadian wares'

    def handle(self, *args, **options):
        if not  Currency.objects.filter(name='یوان چین').exists():
            currency = Currency.objects.create(name='یوان چین', exchange_rate_to_toman=8750)
        else:
            currency = Currency.objects.filter(name='یوان چین').first()


        for product in Product.objects.all():
            if product.brand:
                if product.brand.made_in == 'چین':
                    product.currency = currency
                    product.save()
                    print('product currency set')




