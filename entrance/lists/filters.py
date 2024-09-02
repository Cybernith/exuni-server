import django_filters
from django_filters import rest_framework as filters, CharFilter, BooleanFilter

from entrance.models import EntrancePackage
from helpers.filters import BASE_FIELD_FILTERS, filter_created_by_name


class EntrancePackageFilter(filters.FilterSet):
    created_by__name = CharFilter(method=filter_created_by_name)
    created_by__name__icontains = CharFilter(method=filter_created_by_name)

    class Meta:
        model = EntrancePackage
        fields = {
            'id': ['exact', 'in'],
            'manager': ['exact', 'in'],
            'supplier': ['exact', 'in'],
            'store': ['exact', 'in'],
            'is_received': ['exact'],
            'is_verified': ['exact'],
            'name': BASE_FIELD_FILTERS,
            'registration_date': BASE_FIELD_FILTERS,
            'registration_time': BASE_FIELD_FILTERS,
            'explanation': BASE_FIELD_FILTERS,
        }
