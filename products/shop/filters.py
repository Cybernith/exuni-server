from django.db.models import Q

from helpers.filters import BASE_FIELD_FILTERS
from products.models import Product
from django_filters import rest_framework as filters
import django_filters


class ShopProductFilter(filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name='current_price__price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='current_price__price', lookup_expr='lte')
    min_inventory = django_filters.NumberFilter(field_name='current_inventory__inventory', lookup_expr='gte')
    max_inventory = django_filters.NumberFilter(field_name='current_inventory__inventory', lookup_expr='lte')
    in_stock = django_filters.BooleanFilter(method='filter_in_stock')
    properties = filters.CharFilter(method='filter_properties')
    properties_in = filters.CharFilter(method='filter_properties_in')

    class Meta:
        model = Product
        fields = {
            'id': ('exact',),
            'product_id': BASE_FIELD_FILTERS,
            'name': BASE_FIELD_FILTERS,
            'brand': ('exact', 'in'),
            'category': ('exact', 'in'),

        }

        def filter_in_stock(self, queryset, name, value):
            if value:
                return queryset.filter(current_inventory__inventory__gt=0)
            return queryset.filter(
                Q(current_inventory__inventory__lte=0) | Q(current_inventory__inventory__isnull=True)
            )

        def filter_properties(self, queryset, name, value):
            try:
                ids = [int(i.strip()) for i in value.split(',') if i.strip().isdigit()]
            except ValueError:
                return queryset.none()

            for property_id in ids:
                queryset.filter(perperties__id=property_id)

            return queryset

        def filter_properties_in(self, queryset, name, value):
            try:
                ids = [int(i.strip()) for i in value.split(',') if i.strip().isdigit()]
            except ValueError:
                return queryset.none()

            return queryset.filter(perperties__id__in=ids)
