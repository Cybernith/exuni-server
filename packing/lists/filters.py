from django_filters import rest_framework as filters

from helpers.filters import BASE_FIELD_FILTERS

from packing.models import OrderPackage


class OrderPackageFilter(filters.FilterSet):

    class Meta:
        model = OrderPackage
        fields = {
            'id': ('exact',),
            'business': ('exact',),
            'customer': ('exact',),
            'is_packaged': ('exact',),
            'is_shipped': ('exact',),
            'customer_name': BASE_FIELD_FILTERS,
            'phone': BASE_FIELD_FILTERS,
            'address': BASE_FIELD_FILTERS,
            'postal_code': BASE_FIELD_FILTERS,
        }
