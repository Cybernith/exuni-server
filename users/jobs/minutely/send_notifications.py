import datetime

from django.db.models import Q
from django_extensions.management.jobs import MinutelyJob

from users.models import Notification


class Job(MinutelyJob):
    help = "Send scheduled notifications"

    def execute(self):
        notifications = Notification.objects.filter(
            Q(
                Q(
                    send_date__lt=datetime.date.today()
                ) | Q(
                    send_date=datetime.date.today(),
                    send_time__lte=datetime.datetime.now().time().strftime('%H:%M')
                ) | Q(
                    send_date=None,
                    send_time=None
                )
            ),
            is_sent=False,

        ).exclude(
            Q(has_schedule=False)
            & ~Q(type=Notification.REMINDER)
        ).all()

        for notification in notifications:
            notification.create_user_notifications()
