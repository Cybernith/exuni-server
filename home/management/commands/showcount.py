import jdatetime
from django.core.management import BaseCommand

from financial_management.models import Payment


class Command(BaseCommand):
    help = 'expired pending orders'

    def handle(self, *args, **options):
        year, month, day = map(int, '1404-05-17'.split('-'))
        jdate = jdatetime.date(year, month, day)
        end = jdate.togregorian()

        year, month, day = map(int, '1404-05-1'.split('-'))
        jdate = jdatetime.date(year, month, day)
        start = jdate.togregorian()
        payments = Payment.objects.filter(status='pe', paid_at__date__lte=end, paid_at__date__gte=start)
        customer_ids = payments.values_list('user_id', flat=True).distinct()

        print(len(customer_ids))
