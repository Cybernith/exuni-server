import jdatetime
from django.core.management import BaseCommand
from shop.models import ShopOrder


class Command(BaseCommand):
    help = 'expired pending orders'

    def handle(self, *args, **options):
        year, month, day = map(int, '1404-05-06'.split('-'))
        jdate = jdatetime.date(year, month, day)
        start = jdate.togregorian()

        year, month, day = map(int, '1404-05-12'.split('-'))
        jdate = jdatetime.date(year, month, day)
        end = jdate.togregorian()
        orders = ShopOrder.objects.filter(status__in=['pa', 'pr'], date_time__date__lte=end, date_time__date__gte=start)
        customer_ids = orders.values_list('customer_id', flat=True).distinct()

        print(
            ShopOrder.objects.filter(
                status__in=['pa', 'pr'], date_time__date__lte=end, date_time__date__gte=start
            ).count()
        )

        print(len(customer_ids))
