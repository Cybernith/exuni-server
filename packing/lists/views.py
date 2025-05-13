from django.db.models import Q
from rest_framework import generics
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated

from affiliate.views import get_business_from_request
from helpers.auth import BasicObjectPermission
from affiliate.models import AffiliateFactor
from helpers.functions import get_current_user
from packing.lists.filters import OrderPackageFilter
from packing.models import OrderPackage
from packing.serializers import OrderPackageSerializer


class OrderPackageWithoutAdminListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)

    permission_codename = "get.order_package"

    serializer_class = OrderPackageSerializer
    filterset_class = OrderPackageFilter
    ordering_fields = '__all__'
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return OrderPackage.objects.filter(packing_admin__isnull=True)


class OrderPackageListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)

    permission_codename = "get.order_package"

    serializer_class = OrderPackageSerializer
    filterset_class = OrderPackageFilter
    ordering_fields = '__all__'
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return OrderPackage.objects.all()


class WaitingForPackingOrdersListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)

    permission_codename = "get.order_package"

    serializer_class = OrderPackageSerializer
    filterset_class = OrderPackageFilter
    ordering_fields = '__all__'
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return OrderPackage.objects.filter(Q(packing_admin=get_current_user()) & Q(is_packaged=False))


class WaitingForShippingOrdersListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)

    permission_codename = "get.order_package"

    serializer_class = OrderPackageSerializer
    filterset_class = OrderPackageFilter
    ordering_fields = '__all__'
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return OrderPackage.objects.filter(Q(packing_admin=get_current_user()) &
                                           Q(is_packaged=True) &
                                           Q(is_shipped=False)
                                           )


class AdminPackingReportListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)

    permission_codename = "get.order_package"

    serializer_class = OrderPackageSerializer
    filterset_class = OrderPackageFilter
    ordering_fields = '__all__'
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return OrderPackage.objects.filter(Q(packing_admin=get_current_user()) &
                                           Q(is_packaged=True) &
                                           Q(is_shipped=True)
                                           )


class AffiliateAdminOrderPackagesReportListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)

    permission_codename = "get.order_package"

    serializer_class = OrderPackageSerializer
    filterset_class = OrderPackageFilter
    ordering_fields = '__all__'
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return OrderPackage.objects.filter(business__admin=get_current_user())

