import jdatetime

from financial_management.models import Wallet, Payment
from helpers.sms import Sms
from django.core.management import BaseCommand

from users.models import User


class Command(BaseCommand):
    help = 'expired pending orders'

    def handle(self, *args, **options):
        year, month, day = map(int, '1404-05-17'.split('-'))
        jdate = jdatetime.date(year, month, day)
        end = jdate.togregorian()

        year, month, day = map(int, '1404-05-1'.split('-'))
        jdate = jdatetime.date(year, month, day)
        start = jdate.togregorian()
        payments = Payment.objects.filter(status='pe', created_at__date__lte=end, created_at__date__gte=start)[:500]
        customer_ids = payments.values_list('user_id', flat=True).distinct()
        for customer in User.objects.filter(id__in=customer_ids):
            sms_lines = [
                "اکسونی ",
                " {} همراه همیشگی ما".format(customer.username),
                "اختلال پرداخت و ویرایش سفارش‌ها برطرف شد!",
                "همین الان سفارشت رو ثبت کن ",
                "یه سر به کیف پولت تو اکسونی بزن، شاید سورپرایز شدی 😉",
            ]
            sms_text = "\n".join(sms_lines)
            Sms.send(phone=customer.username, message=sms_text)
