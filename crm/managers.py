from django.db import models

from crm.models import UserNotification


class UserNotificationQuerySet(models.QuerySet):
    def mark_all_as_read(self):
        return self.filter(notification_status=UserNotification.NOT_READ).update(
            notification_status=UserNotification.READ
        )

    def unread(self):
        return self.filter(notification_status=UserNotification.NOT_READ)

    def mark_all_as_un_read(self):
        return self.filter(
            notification_status=UserNotification.PENDING
        ).update(notification_status=UserNotification.NOT_READ)

    def pending(self):
        return self.filter(notification_status=UserNotification.PENDING)


class UserNotificationManager(models.Manager):
    def get_queryset(self):
        return UserNotificationQuerySet(self.model, using=self._db)

    def mark_all_as_read_for_user(self, user):
        return self.get_queryset().filter(user=user).mark_all_as_read()

    def mark_all_as_un_read_for_user(self, user):
        return self.get_queryset().filter(user=user).mark_all_as_un_read()

