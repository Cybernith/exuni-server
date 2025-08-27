from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated

from entrance.lists.filters import EntrancePackageFilter, StoreReceiptFilter, ChinaEntrancePackageFilter, \
    InsertedPackageDeliveryItemFilter, ChinaEntrancePackageDeliveryFilter
from entrance.models import EntrancePackage, StoreReceipt, ChinaEntrancePackage, ChinaEntrancePackageDeliveryItem, \
    ChinaEntrancePackageDelivery
from entrance.serializers import EntrancePackageListSerializer, StoreReceiptListSerializer, \
    ChinaEntrancePackageSerializer, PendingChinaEntrancePackageSerializer, InsertedPackageDeliveryItemSerializer, \
    ChinaEntrancePackageDeliveryCreateSerializer
from helpers.auth import BasicCRUDPermission, BasicObjectPermission
from rest_framework import generics


class EntrancePackageListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, BasicCRUDPermission)
    permission_codename = "get.entrance_packages"

    serializer_class = EntrancePackageListSerializer

    pagination_class = LimitOffsetPagination

    ordering_fields = '__all__'
    filterset_class = EntrancePackageFilter
    search_fields = EntrancePackageFilter.Meta.fields.keys()

    def get_queryset(self):
        return EntrancePackage.objects.hasAccess('get').all()


class StoreReceiptListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, BasicCRUDPermission)
    permission_codename = "get.entrance_packages"

    serializer_class = StoreReceiptListSerializer

    pagination_class = LimitOffsetPagination

    ordering_fields = '__all__'
    filterset_class = StoreReceiptFilter
    search_fields = StoreReceiptFilter.Meta.fields.keys()

    def get_queryset(self):
        return StoreReceipt.objects.hasAccess('get').all()


class ChinaEntrancePackagePackageListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)

    serializer_class = ChinaEntrancePackageSerializer
    filterset_class = ChinaEntrancePackageFilter
    ordering_fields = '__all__'
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return ChinaEntrancePackage.objects.all().prefetch_related('items')


class PendingChinaEntrancePackagePackageListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)

    serializer_class = PendingChinaEntrancePackageSerializer
    filterset_class = ChinaEntrancePackageFilter
    ordering_fields = '__all__'
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return ChinaEntrancePackage.objects.all().prefetch_related('items')


class InsertedPackageDeliveryItemListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)

    serializer_class = InsertedPackageDeliveryItemSerializer
    filterset_class = InsertedPackageDeliveryItemFilter
    ordering_fields = '__all__'
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return ChinaEntrancePackageDeliveryItem.objects.filter(inserted=True, verified=False)


class ChinaEntrancePackageDeliveryListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)

    serializer_class = ChinaEntrancePackageDeliveryCreateSerializer
    filterset_class = ChinaEntrancePackageDeliveryFilter
    ordering_fields = '__all__'
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return ChinaEntrancePackageDelivery.objects.all()

