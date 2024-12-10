from rest_framework import generics
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated

from affiliate.views import get_business_from_request
from helpers.auth import BasicObjectPermission
from affiliate.models import AffiliateFactor
from packing.lists.filters import OrderPackageFilter
from packing.models import OrderPackage
from packing.serializers import OrderPackageSerializer


class OrderPackageWithoutAdminListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)

    permission_codename = "get.affiliate_factor"

    serializer_class = OrderPackageSerializer
    filterset_class = OrderPackageFilter
    ordering_fields = '__all__'
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return OrderPackage.objects.filter(packing_admin__isnull=True)
