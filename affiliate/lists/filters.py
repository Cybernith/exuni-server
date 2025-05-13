from django_filters import rest_framework as filters

from helpers.filters import BASE_FIELD_FILTERS

from affiliate.models import AffiliateFactor
from users.models import User


def status_display_contains_filter(queryset, name, value):
    statuses = {
        'ثبت اولیه': AffiliateFactor.INITIAL_REGISTRATION_STAGE,
        'پرداخت شده': AffiliateFactor.PAID,
    }
    for status in statuses:
        if value in status:
            return queryset.filter(status=statuses[status])
    return queryset.none()

def status_display_filter(queryset, name, value):
    statuses = {
        'ثبت اولیه': AffiliateFactor.INITIAL_REGISTRATION_STAGE,
        'پرداخت شده': AffiliateFactor.PAID,
    }
    for status in statuses:
        if value == status:
            return queryset.filter(status=statuses[status])
    return queryset.none()

def business_name_filter(queryset, name, value):
    return queryset.filter(business_name=value)

def business_name_contains_filter(queryset, name, value):
    return queryset.filter(business_name__icontains=value)


class AffiliateFactorFilter(filters.FilterSet):
    business_name = filters.CharFilter(method=business_name_filter)
    business_name__icontains = filters.CharFilter(method=business_name_contains_filter)
    status_display = filters.CharFilter(method=status_display_filter)
    status_display__icontains = filters.CharFilter(method=status_display_contains_filter)

    class Meta:
        model = AffiliateFactor
        fields = {
            'id': ('exact',),
            'business': ('exact',),
            'customer': ('exact',),
            'status': ('exact',),
            'customer_name': BASE_FIELD_FILTERS,
            'phone': BASE_FIELD_FILTERS,
            'address': BASE_FIELD_FILTERS,
            'postal_code': BASE_FIELD_FILTERS,
            'is_paid': ('exact',),
        }


class AffiliateCustomersFilter(filters.FilterSet):

    class Meta:
        model = User
        fields = {
            'id': ('exact',),
            'first_name': BASE_FIELD_FILTERS,
            'last_name': BASE_FIELD_FILTERS,
            'username': BASE_FIELD_FILTERS,
            'mobile_number': BASE_FIELD_FILTERS,

        }


