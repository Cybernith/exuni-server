from django_filters import rest_framework as filters

from helpers.filters import BASE_FIELD_FILTERS

from affiliate.models import AffiliateFactor

def business_name_filter(queryset, name, value):
    return queryset.filter(business_name=value)

def business_name_contains_filter(queryset, name, value):
    return queryset.filter(business_name__icontains=value)


class AffiliateFactorFilter(filters.FilterSet):
    business_name = filters.CharFilter(method=business_name_filter)
    business_name__icontains = filters.CharFilter(method=business_name_contains_filter)

    class Meta:
        model = AffiliateFactor
        fields = {
            'id': ('exact',),
            'business': ('exact',),
            'customer': ('exact',),
            'customer_name': BASE_FIELD_FILTERS,
            'phone': BASE_FIELD_FILTERS,
            'address': BASE_FIELD_FILTERS,
            'postal_code': BASE_FIELD_FILTERS,
            'is_paid': ('exact',),
        }

