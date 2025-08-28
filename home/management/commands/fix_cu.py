from django.core.management import BaseCommand
import csv

from main.models import Currency
from products.models import Product, Brand


class Command(BaseCommand):
    help = "Read DO and DM columns from CSV and print with row index"

    def handle(self, *args, **options):
        products = Product.objects.all()
        yoan = Currency.objects.get(id=17)
        hero_brand = Brand.objects.get(id=271)
        hero = products.filter(name__icontains='HERORANGE')
        hero.update(brand=hero_brand, currency=yoan)

