from django.db.models import QuerySet, Q
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from helpers.auth import BasicCRUDPermission
from users.filters import UserNotificationFilter, NotificationFilter
from users.models import UserNotification, Notification
from users.serializers import UserNotificationSerializer, SendNotificationSerializer, ReminderNotificationSerializer


class UserNotificationListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserNotificationSerializer
    filterset_class = UserNotificationFilter
    ordering_fields = '__all__'
    pagination_class = LimitOffsetPagination

    def get_queryset(self) -> QuerySet:
        return UserNotification.objects.filter(user=self.request.user).order_by('-status', 'id')


class ChangeUserNotificationStatusView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        data = request.data
        user = request.user

        user_notification = get_object_or_404(UserNotification, user=user, pk=data.get('id'))
        user_notification.status = data.get('new_status')
        user_notification.save()

        return Response([])


class SendNotificationModelView(ModelViewSet):
    permission_classes = (IsAuthenticated, BasicCRUDPermission)
    permission_codename = 'send.notification'
    serializer_class = SendNotificationSerializer
    ordering_fields = '__all__'
    pagination_class = LimitOffsetPagination
    filterset_class = NotificationFilter

    def get_queryset(self) -> QuerySet:
        return Notification.objects.filter(created_by=self.request.user, type=Notification.SEND_BY_USER)

    def perform_create(self, serializer: SendNotificationSerializer) -> None:
        serializer.save(
            type=Notification.SEND_BY_USER,
            forwarder_company=self.request.user.active_company
        )
        notification = Notification.objects.get(id=serializer.data['id'])
        if not notification.has_schedule and not notification.type == Notification.REMINDER:
            notification.create_user_notifications()


class ReminderNotificationModelView(ModelViewSet):
    permission_classes = (IsAuthenticated, )
    serializer_class = ReminderNotificationSerializer
    ordering_fields = '__all__'
    pagination_class = LimitOffsetPagination
    filterset_class = NotificationFilter

    def get_queryset(self) -> QuerySet:
        return Notification.objects.filter(created_by=self.request.user, type=Notification.REMINDER)

    def perform_create(self, serializer: ReminderNotificationSerializer) -> None:
        serializer.save(
            receivers=[self.request.user],
            type=Notification.REMINDER,
            has_schedule=True,
            show_pop_up=True,
        )


class SendNotificationListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, BasicCRUDPermission)
    permission_codename = 'send.notification'
    serializer_class = SendNotificationSerializer
    ordering_fields = '__all__'
    pagination_class = LimitOffsetPagination
    filterset_class = NotificationFilter

    def get_queryset(self):
        return Notification.objects.filter(created_by=self.request.user, type=Notification.SEND_BY_USER)


class ReminderNotificationListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = ReminderNotificationSerializer
    ordering_fields = '__all__'
    pagination_class = LimitOffsetPagination
    filterset_class = NotificationFilter

    def get_queryset(self):
        return Notification.objects.filter(created_by=self.request.user, type=Notification.REMINDER)
