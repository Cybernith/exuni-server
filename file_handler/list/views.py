from rest_framework import generics
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated

from file_handler.list.filters import ExtractedPostReportFilter, ExtractedPostReportItemFilter
from file_handler.models import ExtractedPostReport, ExtractedPostReportItem
from file_handler.serializers import ExtractedPostReportItemSerializer, ExtractedPostReportSerializer
from helpers.auth import BasicObjectPermission


class ExtractedPostReportListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)

    serializer_class = ExtractedPostReportSerializer
    filterset_class = ExtractedPostReportFilter
    ordering_fields = '__all__'
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return ExtractedPostReport.objects.filter(
            items__status=ExtractedPostReportItem.ORDER_NOT_AVAILABLE
        ).distinct()


class ExtractedPostReportItemListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)

    serializer_class = ExtractedPostReportItemSerializer
    filterset_class = ExtractedPostReportItemFilter
    ordering_fields = '__all__'
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return ExtractedPostReportItem.objects.all()
