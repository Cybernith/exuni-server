from django_filters import rest_framework as filters

from helpers.filters import BASE_FIELD_FILTERS
from products.models import Brand, Avail, ProductProperty, Category, Product, ProductGallery


def supplier_name_filter(queryset, name, value):
    return queryset.filter(supplier__name__contains=value)

class BrandFilter(filters.FilterSet):
    supplier_name = filters.CharFilter(method=supplier_name_filter)

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


class CategoryFilter(filters.FilterSet):

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
            'brand': ('exact',),
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
            'category': ('exact',),

        }
