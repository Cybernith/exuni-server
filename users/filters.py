from django_filters import rest_framework as filters
from users.models import UserNotification, Notification


class UserNotificationFilter(filters.FilterSet):
    class Meta:
        model = UserNotification
        fields = {
            'notification__title': ['exact', 'contains'],
            'notification__explanation': ['exact', 'contains'],
            'notification__created_at': ['exact', 'gte', 'lte'],
        }


class NotificationFilter(filters.FilterSet):
    class Meta:
        model = Notification
        fields = {
            'title': ['exact', 'contains'],
            'explanation': ['exact', 'contains'],
            'created_at': ['exact', 'gte', 'lte'],
        }
