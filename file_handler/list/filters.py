from django_filters import rest_framework as filters

from file_handler.models import ExtractedPostReport, ExtractedPostReportItem
from helpers.filters import BASE_FIELD_FILTERS


class ExtractedPostReportFilter(filters.FilterSet):
    class Meta:
        model = ExtractedPostReport
        fields = {
            'id': ['exact', 'in'],
            'name': BASE_FIELD_FILTERS,
            'date': BASE_FIELD_FILTERS,
            'created_at': BASE_FIELD_FILTERS,
        }


class ExtractedPostReportItemFilter(filters.FilterSet):
    class Meta:
        model = ExtractedPostReportItem
        fields = {
            'id': ['exact', 'in'],
            'extracted_report': ['exact', 'in'],
            'status': ['exact', 'in'],
            'post_tracking_code': BASE_FIELD_FILTERS,
            'created_at': BASE_FIELD_FILTERS,
            'price': BASE_FIELD_FILTERS,
        }
