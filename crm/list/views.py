from django.core.exceptions import PermissionDenied
from rest_framework import generics
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated

from crm.list.filters import ShopProductViewLogFilter
from crm.models import ShopProductViewLog
from crm.serializer import ShopProductViewLogSerializer
from helpers.functions import get_current_user


class ShopProductViewLogReportListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated)

    serializer_class = ShopProductViewLogSerializer
    filterset_class = ShopProductViewLogFilter
    ordering_fields = '__all__'
    pagination_class = LimitOffsetPagination
    ordering = ['-created_at']

    def get_queryset(self):
        if get_current_user().is_superuser:
            return ShopProductViewLog.objects.all()
        raise PermissionDenied('you dont have access')
