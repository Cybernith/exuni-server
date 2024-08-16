from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from helpers.auth import BasicCRUDPermission


class RetrieveUpdateDestroyAPIViewWithAutoFinancialYear(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated, BasicCRUDPermission)

    def get_queryset(self):
        return self.get_serializer_class().Meta.model.objects.hasAccess(self.request.method)
