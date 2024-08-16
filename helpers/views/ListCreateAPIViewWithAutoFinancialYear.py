from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer

from helpers.auth import BasicCRUDPermission


class ListCreateAPIViewWithAutoFinancialYear(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated, BasicCRUDPermission)

    def get_queryset(self):
        return self.serializer_class.Meta.model.objects.hasAccess(self.request.method)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)

        self.created(serializer.instance, request)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer: BaseSerializer) -> None:
        serializer.save(
            financial_year=self.request.user.active_financial_year
        )

    def created(self, instance, request):
        pass
