from django.db.models import Q
from django_filters import rest_framework as filters

from helpers.filters import BASE_FIELD_FILTERS
from shop.models import ShopOrder


class ShopOrderStatusFilter(filters.CharFilter):
    def filter(self, qs, value):
        if not value:
            return qs

        internal_codes = [val for val, _ in ShopOrder.STATUS_CHOICES]
        if value in internal_codes:
            return super().filter(qs, value)

        reverse_map = {label: val for val, label in ShopOrder.STATUS_CHOICES}
        if value in reverse_map:
            return super().filter(qs, reverse_map[value])

        filtered_values = [
            val for val, label in ShopOrder.STATUS_CHOICES if value in label
        ]
        if filtered_values:
            return qs.filter(**{f'{self.field_name}__in': filtered_values})

        return qs.none()


class CustomerFilter(filters.CharFilter):
    def filter(self, qs, value):
        if not value:
            return qs

        return qs.filter(
            Q(customer__first_name__icontains=value) |
            Q(customer__last_name__icontains=value) |
            Q(customer__mobile_number__icontains=value)
        )


class DiscountByCodeFilter(filters.CharFilter):
    def filter(self, qs, value):
        if not value:
            return qs

        return qs.filter(discount_code__code__icontains=value)


class ProductFilter(filters.CharFilter):
    def filter(self, qs, value):
        if not value:
            return qs

        return qs.filter(
            Q(items__product__name__icontains=value) |
            Q(items__product__sixteen_digit_code__icontains=value)
        ).distinct()


class SmartShipmentCityFilter(filters.CharFilter):
    def filter(self, qs, value):
        if not value:
            return qs
        return qs.filter(
            Q(shipment_address__city__icontains=value) |
            Q(shipment_address__address__icontains=value) |
            Q(shipment_address__zip_code__icontains=value) |
            Q(shipment_address__state__icontains=value)
        ).distinct()


class ShopOrderFilter(filters.FilterSet):
    status_contains = ShopOrderStatusFilter()
    customer_contains = CustomerFilter()
    discount_code_contains = DiscountByCodeFilter()
    product_contains = ProductFilter()
    shipment_contains = SmartShipmentCityFilter()

    class Meta:
        model = ShopOrder
        fields = {
            'id': ('exact',),
            'is_sent': ('exact',),
            'status': ('exact',),
            'discount_code': ('exact',),
            'date_time': BASE_FIELD_FILTERS,
            'post_date_time': BASE_FIELD_FILTERS,
            'post_tracking_code': BASE_FIELD_FILTERS,
            'exuni_tracking_code': BASE_FIELD_FILTERS,
            'total_price': BASE_FIELD_FILTERS,
            'total_product_quantity': BASE_FIELD_FILTERS,
        }

