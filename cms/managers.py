from django.db import models
import datetime

from django.db.models import Q


class CMSCustomManager(models.Manager):
    def current_by_datetime(self):
        now = datetime.datetime.now()
        return self.get_queryset().filter(
            (Q(to_date_time__lte=now) & Q(from_date_time__gte=now)) |
            (Q(to_date_time__lte=now) & Q(from_date_time__isnull=True)) |
            (Q(to_date_time__isnull=True) & Q(from_date_time__gte=now)) |
            (Q(to_date_time__isnull=True) & Q(from_date_time__isnull=True))
        )