from django.db.models import Q
from django_filters import rest_framework as filters

from helpers.filters import BASE_FIELD_FILTERS
from issues.models import Issue


class IssueFilter(filters.FilterSet):

    class Meta:
        model = Issue
        fields = {
            'id': ('exact',),
            'issue_type': ('exact',),
            'status': ('exact',),
            'created_by': ('exact',),
            'title': BASE_FIELD_FILTERS,
            'description': BASE_FIELD_FILTERS,
            'created_at': BASE_FIELD_FILTERS,
        }
