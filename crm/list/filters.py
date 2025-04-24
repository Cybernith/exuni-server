from crm.models import ShopProductViewLog
from django_filters import rest_framework as filters

from helpers.filters import BASE_FIELD_FILTERS


class ShopProductViewLogFilter(filters.FilterSet):

    class Meta:
        model = ShopProductViewLog
        fields = {
            'id': ('exact',),
            'product': ('exact',),
            'user': ('exact',),
            'ip_address': BASE_FIELD_FILTERS,
            'referer': BASE_FIELD_FILTERS,
            'device_type': BASE_FIELD_FILTERS,
            'created_at': BASE_FIELD_FILTERS,
            'updated_at': BASE_FIELD_FILTERS,
        }
