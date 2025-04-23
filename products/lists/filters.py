from django.db.models import Q
from django_filters import rest_framework as filters

from helpers.filters import BASE_FIELD_FILTERS
from products.models import Brand, Avail, ProductProperty, Category, Product, ProductGallery


def supplier_name_filter(queryset, name, value):
    return queryset.filter(supplier__name=value)

def supplier_name_contains_filter(queryset, name, value):
    return queryset.filter(supplier__name__contains=value)

class BrandFilter(filters.FilterSet):
    supplier_name = filters.CharFilter(method=supplier_name_filter)
    supplier_name__icontains = filters.CharFilter(method=supplier_name_contains_filter)

    class Meta:
        model = Brand
        fields = {
            'id': ('exact',),
            'is_domestic': ('exact',),
            'supplier': ('exact',),
            'name': BASE_FIELD_FILTERS,
            'made_in': BASE_FIELD_FILTERS,
        }


class AvailFilter(filters.FilterSet):

    class Meta:
        model = Avail
        fields = {
            'id': ('exact',),
            'name': BASE_FIELD_FILTERS,
            'explanation': BASE_FIELD_FILTERS,
        }


class ProductPropertyFilter(filters.FilterSet):

    class Meta:
        model = ProductProperty
        fields = {
            'id': ('exact',),
            'name': BASE_FIELD_FILTERS,
            'explanation': BASE_FIELD_FILTERS,
        }


def parent_name_filter(queryset, name, value):
    return queryset.filter(parent__name=value)


def parent_name_contains_filter(queryset, name, value):
    return queryset.filter(parent__name__contains=value)


class CategoryFilter(filters.FilterSet):
    parent_name = filters.CharFilter(method=parent_name_filter)
    parent_name__icontains = filters.CharFilter(method=parent_name_contains_filter)

    class Meta:
        model = Category
        fields = {
            'id': ('exact',),
            'parent': ('exact',),
            'name': BASE_FIELD_FILTERS,
        }


class ProductGalleryFilter(filters.FilterSet):

    class Meta:
        model = ProductGallery
        fields = {
            'id': ('exact',),
            'product': ('exact',),
        }


class ProductFilter(filters.FilterSet):

    class Meta:
        model = Product
        fields = {
            'id': ('exact',),
            'product_id': BASE_FIELD_FILTERS,
            'name': BASE_FIELD_FILTERS,
            'first_inventory': BASE_FIELD_FILTERS,
            'shelf_code': BASE_FIELD_FILTERS,
            'min_inventory': BASE_FIELD_FILTERS,
            'price': BASE_FIELD_FILTERS,
            'shipping_cost': BASE_FIELD_FILTERS,
            'currency': ('exact',),
            'profit_percent': BASE_FIELD_FILTERS,
            'tax_percent': BASE_FIELD_FILTERS,
            'supplier': ('exact',),
            'brand': ('exact', 'in'),
            'explanation': BASE_FIELD_FILTERS,
            'summary_explanation': BASE_FIELD_FILTERS,
            'how_to_use': BASE_FIELD_FILTERS,
            'product_date': BASE_FIELD_FILTERS,
            'expired_date': BASE_FIELD_FILTERS,
            'status': ('exact',),
            'postal_weight': BASE_FIELD_FILTERS,
            'length': BASE_FIELD_FILTERS,
            'width': BASE_FIELD_FILTERS,
            'height': BASE_FIELD_FILTERS,
            # avails many to many filter
            # properties many to many filter
            'category': ('exact', 'in'),

        }

def has_picture_filter(queryset, name, value):
    if value == 'true':
        return queryset.exclude(Q(picture=None) | Q(picture=''))
    else:
        return queryset.filter(Q(picture=None) | Q(picture=''))

def has_explanation_filter(queryset, name, value):
    if value == 'true':
        return queryset.exclude(Q(explanation=None) | Q(explanation=''))
    else:
        return queryset.filter(Q(explanation=None) | Q(explanation=''))


def has_summary_explanation_filter(queryset, name, value):
    if value == 'true':
        return queryset.exclude(Q(summary_explanation=None) | Q(summary_explanation=''))
    else:
        return queryset.filter(Q(summary_explanation=None) | Q(summary_explanation=''))


def has_how_to_use_filter(queryset, name, value):
    if value == 'true':
        return queryset.exclude(Q(how_to_use=None) | Q(how_to_use=''))
    else:
        return queryset.filter(Q(how_to_use=None) | Q(how_to_use=''))


class NoContentProductFilter(filters.FilterSet):
    has_picture = filters.CharFilter(method=has_picture_filter)
    has_explanation = filters.CharFilter(method=has_explanation_filter)
    has_summary_explanation = filters.CharFilter(method=has_summary_explanation_filter)
    has_how_to_use = filters.CharFilter(method=has_how_to_use_filter)

    class Meta:
        model = Product
        fields = {
            'id': ('exact',),
            'name': BASE_FIELD_FILTERS,
            'barcode': BASE_FIELD_FILTERS,
        }
