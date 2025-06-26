from django.core.management import BaseCommand

from main.models import Currency


class Command(BaseCommand):
    help = 'insert currencies'
    currencies = [
        {
            'name': 'دربی(DERBY)',
            'code': '145657',
            'exchange_rate_to_toman': 1,

        },
        {
            'name': 'نئودرم(NEUDERM)',
            'code': '145656',
            'exchange_rate_to_toman': 1,

        },
        {
            'name': 'الارو(Ellaro)',
            'code': '145655',
            'exchange_rate_to_toman': 1,

        },
        {
            'name': 'شون مراقبت پوستی(schon skin care)',
            'code': '145654',
            'exchange_rate_to_toman': 1,

        },
        {
            'name': 'مای مراقبت پوستی ( my skin care)',
            'code': '145644',
            'exchange_rate_to_toman': 1,

        },
        {
            'name': 'تومان کامان پیکسل نینو',
            'code': '126609',
            'exchange_rate_to_toman': 1,

        },
        {
            'name': ' پارس حیان',
            'code': '125677',
            'exchange_rate_to_toman': 1,

        },
        {
            'name': 'درهم امارات',
            'code': '48794',
            'exchange_rate_to_toman': 20000,

        },
        {
            'name': 'دلار',
            'code': '23058',
            'exchange_rate_to_toman': 79000,

        },
        {
            'name': 'تومان',
            'code': '18495',
            'exchange_rate_to_toman': 1.4,

        },
        {
            'name': 'یوان چین',
            'code': '282',
            'exchange_rate_to_toman': 13600,

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
            print('currency added')






