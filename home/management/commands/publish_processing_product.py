from django.core.management import BaseCommand
from django.db.models import Q

from products.models import Product


class Command(BaseCommand):
    help = 'publish'



    def handle(self, *args, **options):
        pr = Product.objects.filter(
            Q(status=Product.PROCESSING) &
            Q(product_type=Product.SIMPLE) &
            Q(price__gte=1) &
            ~Q(name='without name') &
            Q(name__isnull=False)
        )
        print(pr.count())

        varb = Product.objects.filter(
            Q(status=Product.PROCESSING) &
            Q(product_type=Product.VARIABLE) &
            ~Q(name='without name') &
            Q(name__isnull=False)
        )
        print(varb.count())

        var = Product.objects.filter(
            Q(status=Product.PROCESSING) &
            Q(product_type=Product.VARIATION) &
            Q(price__gte=1) &
            ~Q(name='without name') &
            Q(name__isnull=False) &
            Q(variation_of__isnull=False)
        )
        print(var.count())

        varb.update(status=Product.PUBLISHED)
        pr.update(status=Product.PUBLISHED)
        var.update(status=Product.PUBLISHED)

