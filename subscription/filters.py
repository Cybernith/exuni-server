from django_filters import rest_framework as filters
from helpers.filters import BASE_FIELD_FILTERS
from subscription.models import Transaction


class TransactionFilter(filters.FilterSet):
    class Meta:
        model = Transaction
        fields = {
            'id': ['exact'],
            'type': BASE_FIELD_FILTERS,
            'amount': BASE_FIELD_FILTERS,
            'datetime': BASE_FIELD_FILTERS,
        }
