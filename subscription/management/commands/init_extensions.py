from django.contrib.auth.models import Permission
from django.core.management.base import BaseCommand
from django.db.models import Q

from subscription.models import Extension

extensions = [
    {
        'name': 'EIGHT_LEVEL_ACCOUNTING',
        'price': 2800000,
        'is_permanent': True
    },
    {
        'name': 'ONLINE_SUPPORT',
        'price': 480000,
        'is_permanent': False
    },
    {
        'name': 'MOADIAN',
        'price': 780000,
        'is_permanent': False
    },
    {
        'name': 'PROFESSIONAL_DASHBOARD',
        'price': 370000,
        'is_permanent': False
    },
    {
        'name': 'WOOCOMMERCE_API',
        'price': 800000,
        'is_permanent': False
    },
    {
        'name': 'CREATE_NEW_ACCOUNT',
        'price': 800000,
        'is_permanent': False
    },
    {
        'name': 'CREATE_NEW_CHEQUE',
        'price': 500000,
        'is_permanent': False
    },
    {
        'name': 'CREATE_NEW_IMPREST',
        'price': 700000,
        'is_permanent': False
    },
    {
        'name': 'PROFESSIONAL_REPORT',
        'price': 980000,
        'is_permanent': False
    },
    {
        'name': 'DAEMI_SYSTEM',
        'price': 1400000,
        'is_permanent': True
    },
    {
        'name': 'FIRST_IN_FIRST_OUT_PRICING',
        'price': 700000,
        'is_permanent': True
    },
    {
        'name': 'UNLIMITED_CREATE_PERSON',
        'price': 190000,
        'is_permanent': False
    },
    {
        'name': 'UNLIMITED_CREATE_TREASURY_ACCOUNT',
        'price': 100000,
        'is_permanent': False
    },
    {
        'name': 'INVENTORY_CLERK',
        'price': 800000,
        'is_permanent': False
    },
    {
        'name': 'CONSUMPTION_WARE_FACTOR',
        'price': 500000,
        'is_permanent': False
    },
    {
        'name': 'RECEIPT_AND_REMITTANCE',
        'price': 600000,
        'is_permanent': False
    },
    {
        'name': 'GROUP_PRICE_CHANGE',
        'price': 400000,
        'is_permanent': False
    },
]


class Command(BaseCommand):
    help = 'init extensions'

    def handle(self, *args, **options):
        payroll_extension = Extension.objects.get(pk=1)
        payroll_extension.update(price=1900000, is_permanent=False, name=Extension.PAYROLL)

        for extension in extensions:
            Extension.objects.update_or_create(name=extension['name'], defaults=extension)
            # if Extension.objects.filter(name=extension['name']).exists():
            #     current_extension = Extension.objects.get(name=extension['name'])
            #     current_extension.update(price=extension['price'], is_permanent=extension['is_permanent'])
            # else:
            #     Extension.objects.create(
            #         name=extension['name'],
            #         price=extension['price'],
            #         is_permanent=extension['is_permanent'],
            #     )







