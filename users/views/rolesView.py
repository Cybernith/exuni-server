from django.contrib.auth.models import Permission
from django.db.models import QuerySet
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer
from rest_framework.views import APIView

from helpers.auth import BasicCRUDPermission
from users.models import Role
from users.serializers import RoleSerializer, PermissionListSerializer


class PermissionListView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        queryset = Permission.objects.all().order_by('pk')
        excludes = ('auth', 'admin', 'authtoken', 'sessions', 'contenttypes', 'phoneverification')

        for app_label in excludes:
            queryset = queryset.exclude(content_type__app_label=app_label)

        return Response(PermissionListSerializer(queryset.all(), many=True).data)


class RoleListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, BasicCRUDPermission)
    permission_basename = 'role'
    serializer_class = RoleSerializer

    def get_queryset(self):
        return Role.objects.hasAccess(self.request.method).filter(company=self.request.user.active_company)


class RoleCreateView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated, BasicCRUDPermission)
    permission_basename = 'role'
    queryset = Role.objects.all()
    serializer_class = RoleSerializer

    def perform_create(self, serializer: BaseSerializer) -> None:
        serializer.save(
            company=self.request.user.active_company,
        )


class RoleUpdateView(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated, BasicCRUDPermission)
    permission_basename = 'role'
    serializer_class = RoleSerializer

    def get_queryset(self):
        return Role.objects.hasAccess(self.request.method).filter(company=self.request.user.active_company)


class RoleDestroyView(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated, BasicCRUDPermission)
    permission_basename = 'role'
    serializer_class = RoleSerializer

    def get_queryset(self):
        return Role.objects.hasAccess(self.request.method).filter(company=self.request.user.active_company)
