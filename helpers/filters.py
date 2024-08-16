from django.db.models import Q, F, Value
from django.db.models.functions.text import Concat

BASE_FIELD_FILTERS = ['exact', 'in', 'icontains', 'lt', 'gt', 'lte', 'gte']


def filter_created_by_name(queryset, name, value):
    queryset = queryset.annotate(
        created_by__name=Concat('created_by__first_name', Value(' '), 'created_by__last_name')
    )
    return queryset.filter(**{name: value})
