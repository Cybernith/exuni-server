import jdatetime

from helpers.sms import Sms
from django.core.management import BaseCommand

from users.models import User


class Command(BaseCommand):
    help = 'expired pending orders'

    def handle(self, *args, **options):
        from datetime import datetime

        start = datetime(2025, 8, 28, 20, 0)
        end = datetime(2025, 8, 29, 22, 0)

        users = User.objects.filter(
            verificationCodes__created_at__gte=start,
            verificationCodes__created_at__lte=end
        ).distinct()
        print(users.count())
        sms_lines = [
            "اکسونی ",
            "همراه همیشگی اکسونی",
            " مشکل ارسال پیامک ورود رفع شد… یک عالمه سورپرایز منتظر خرید توعه",
        ]
        sms_text = "\n".join(sms_lines)
        for user in users:
            Sms.send(phone=user.username, message=sms_text)


