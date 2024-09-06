from django_filters import rest_framework as filters

from main.models import Business, Store, Currency, Supplier
from helpers.filters import BASE_FIELD_FILTERS


def business_type_filter(queryset, name, value):
    business_types = {
        'فروشگاه اینترنتی': Business.ONLINE_MARKET,
        'فروشنده پورسانتی': Business.COMMISSION_SELLER,
        'فروشگاه نمایندگی': Business.REPRESENTATION_MARKET,
    }
    query = queryset.filter(pk=None)
    for business_type in business_types:
        if value in business_type:
            query = queryset.filter(business_type=business_types[business_type])
    return query


class BusinessFilter(filters.FilterSet):
    business_type_display = filters.CharFilter(method=business_type_filter)

    class Meta:
        model = Business
        fields = {
            'id': ('exact',),
            'name': BASE_FIELD_FILTERS,
            'domain_address': BASE_FIELD_FILTERS,
            'about_us': BASE_FIELD_FILTERS,
            'address': BASE_FIELD_FILTERS,
            'business_type': ('exact',),
            'api_token': ('exact',),
        }


class StoreFilter(filters.FilterSet):

    class Meta:
        model = Store
        fields = {
            'id': ('exact',),
            'storekeeper': ('exact',),
            'is_central': ('exact',),
            'name': BASE_FIELD_FILTERS,
            'address': BASE_FIELD_FILTERS,
        }


class CurrencyFilter(filters.FilterSet):

    class Meta:
        model = Currency
        fields = {
            'id': ('exact',),
            'name': BASE_FIELD_FILTERS,
            'exchange_rate_to_toman': BASE_FIELD_FILTERS,
        }


class SupplierFilter(filters.FilterSet):

    class Meta:
        model = Supplier
        fields = {
            'id': ('exact',),
            'admin': ('exact',),
            'name': BASE_FIELD_FILTERS,
            'bank_account_number': BASE_FIELD_FILTERS,
            'bank_card_number': BASE_FIELD_FILTERS,
            'bank_sheba_number': BASE_FIELD_FILTERS,
            'address': BASE_FIELD_FILTERS,
            'phone': BASE_FIELD_FILTERS,
        }
