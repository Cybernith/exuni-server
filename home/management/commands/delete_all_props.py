from django.core.management import BaseCommand
from django.db import transaction
from django.db.models import F
from woocommerce import API

from main.models import Currency
from products.models import Product, ProductGallery, Category, Brand, ProductProperty, ProductAttribute, \
    ProductAttributeTerm, ProductPropertyTerm
from server.settings import WC_C_KEY, WC_C_SECRET
from users.models import User
import json
import requests
from django.core.files.base import ContentFile


class Command(BaseCommand):
    help = 'fetch products data'

    def handle(self, *args, **options):
        ProductProperty.objects.all().delete()
        print('terms deleted')
        print(ProductPropertyTerm.objects.all().count)
        ProductPropertyTerm.objects.all().delete()
        print('deleted')
        print(ProductProperty.objects.all().count)
