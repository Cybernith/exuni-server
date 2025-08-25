from rest_framework import generics
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated

from file_handler.list.filters import ExtractedPostReportFilter, ExtractedPostReportItemFilter, \
    ExtractedEntrancePackageFilter, ExtractedEntrancePackageItemFilter
from file_handler.models import ExtractedPostReport, ExtractedPostReportItem, ExtractedEntrancePackage, \
    ExtractedEntrancePackageItem
from file_handler.serializers import ExtractedPostReportItemSerializer, ExtractedPostReportSerializer, \
    ExtractedEntrancePackageReportSerializer, ExtractedEntrancePackageItemSerializer
from helpers.auth import BasicObjectPermission


class ExtractedPostReportListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)

    serializer_class = ExtractedPostReportSerializer
    filterset_class = ExtractedPostReportFilter
    ordering_fields = '__all__'
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return ExtractedPostReport.objects.all().prefetch_related('items', 'items__shop_order')


class ExtractedPostReportItemListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)

    serializer_class = ExtractedPostReportItemSerializer
    filterset_class = ExtractedPostReportItemFilter
    ordering_fields = '__all__'
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return ExtractedPostReportItem.objects.all()


class ExtractedEntrancePackageListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)

    serializer_class = ExtractedEntrancePackageReportSerializer
    filterset_class = ExtractedEntrancePackageFilter
    ordering_fields = '__all__'
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return ExtractedEntrancePackage.objects.filter(is_done=False).prefetch_related('items')


class ExtractedEntrancePackageItemListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)

    serializer_class = ExtractedEntrancePackageItemSerializer
    filterset_class = ExtractedEntrancePackageItemFilter
    ordering_fields = '__all__'
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return ExtractedEntrancePackageItem.objects.all()
