import jdatetime

from financial_management.models import Wallet
from helpers.sms import Sms
from django.core.management import BaseCommand


class Command(BaseCommand):
    help = 'expired pending orders'

    def handle(self, *args, **options):
        from shop.models import ShopOrder
        year, month, day = map(int, '1404-05-06'.split('-'))
        jdate = jdatetime.date(year, month, day)
        start = jdate.togregorian()

        year, month, day = map(int, '1404-05-12'.split('-'))
        jdate = jdatetime.date(year, month, day)
        end = jdate.togregorian()
        shop_orders = ShopOrder.objects.filter(status__in=['pa', 'pr'], date_time__date__lte=end, date_time__date__gte=start).select_related('shipment_address')

        for order in shop_orders:
            detail = order.shipment_address
            sms_lines = [
                "اکسونی ",
                "{} {}  عزیز".format(detail.first_name or '', detail.last_name or ''),
                "با ۱۰ روز صبر شما پردازش و بسته بندی اکسونی هوشمند شد!",
                "این صبر دلیلی برای سرعت، دقت و پردازش بهینه سفارشات شماست",
                "از امروز ارسال سفارشات اکسونی روزانه شد",
                "به پاس شکیبایی شما",
                "مبلغ : 500,000 + ریال",
                "به کیف پول شما واریز شد",
                "از امروز سفارشات در حال ارسال است",
            ]
            sms_text = "\n".join(sms_lines)
            Sms.send(phone=order.customer.username, message=sms_text)

