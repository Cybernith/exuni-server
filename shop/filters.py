from django.db.models import Q
from django_filters import rest_framework as filters

from helpers.filters import BASE_FIELD_FILTERS
from shop.models import ShopOrder


class ShopOrderFilter(filters.FilterSet):
    status_display = filters.CharFilter(method='filter_by_display')

    class Meta:
        model = ShopOrder
        fields = {
            'id': ('exact',),
            'status': ('exact',),
            'total_price': BASE_FIELD_FILTERS,
            'total_product_quantity': BASE_FIELD_FILTERS,
            'offer_price': BASE_FIELD_FILTERS,
            'date_time': BASE_FIELD_FILTERS,
            'post_price': BASE_FIELD_FILTERS,
            'post_date_time': BASE_FIELD_FILTERS,
            'post_tracking_code': BASE_FIELD_FILTERS,
            'exuni_tracking_code': BASE_FIELD_FILTERS,
            'items__product__name': ['icontains'],  # Enables ?items__product__name=iphone
        }

    def filter_by_display(self, queryset, name, value):
        for val, label in ShopOrder.STATUS_CHOICES:
            if label.lower() == value.lower():
                return queryset.filter(status=val)
        return queryset.none()
