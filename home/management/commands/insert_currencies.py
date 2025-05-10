from django.core.management import BaseCommand

from main.models import Currency


class Command(BaseCommand):
    help = 'insert currencies'
    currencies = [
        {
            'name': 'یوان چین',
            'code': '282',
            'exchange_rate_to_toman': 13000,

        },
        {
            'name': 'تومان',
            'code': '18495',
            'exchange_rate_to_toman': 1.1,

        },
        {
            'name': 'تومان پارس حیان',
            'code': '125677',
            'exchange_rate_to_toman': 1,

        },
        {
            'name': 'تومان کامان پیکسل نینو',
            'code': '126609',
            'exchange_rate_to_toman': 1,

        },
        {
            'name': 'دلار',
            'code': '23058',
            'exchange_rate_to_toman': 49000,

        },
        {
            'name': 'درهم امارات',
            'code': '48794',
            'exchange_rate_to_toman': 20000,

        },
    ]

    def handle(self, *args, **options):
        Currency.objects.all().delete()
        for currency in self.currencies:
            Currency.objects.create(
                unique_code=currency['code'],
                name=currency['name'],
                exchange_rate_to_toman=currency['exchange_rate_to_toman'],
            )






