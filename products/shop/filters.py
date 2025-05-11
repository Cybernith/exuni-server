from django.db.models import Q, Count, Avg, Value, FloatField
from django.db.models.functions import Coalesce

from helpers.filters import BASE_FIELD_FILTERS
from products.models import Product, Brand, Category
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


def category_tree_filter(queryset, name, value):
    ids = [int(cat_id) for cat_id in value.split(',') if cat_id != '']
    categories = []
    for cat_id in ids:
        cats = Category.objects.get(pk=cat_id).get_all_descendants()
        categories.extend(cats)
        categories.append(Category.objects.get(pk=cat_id))

    return queryset.filter(category__in=categories)


def top_viewed_filter(queryset, name, value):
    order_by = '-view_count' if value else 'view_count'
    return queryset.annotate(view_count=Count('views_log')).order_by(order_by, '-id')


def top_rated_filter(queryset, name, value):
    order_by = '-avg_rate' if value else 'avg_rate'
    return queryset.annotate(avg_rate=Coalesce(
        Avg('products_rates__level'), Value(0.0), output_field=FloatField())
    ).order_by(order_by)


class ShopProductSimpleFilter(filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    min_inventory = django_filters.NumberFilter(field_name='current_inventory__inventory', lookup_expr='gte')
    max_inventory = django_filters.NumberFilter(field_name='current_inventory__inventory', lookup_expr='lte')
    brand_in = filters.BaseInFilter(
        field_name='brand__id',
        lookup_expr='in'
    )
    category_in = filters.BaseInFilter(
        field_name='category__id',
        lookup_expr='in'
    )
    category_tree = filters.CharFilter(method=category_tree_filter)
    top_viewed = filters.BooleanFilter(method=top_viewed_filter)
    top_rated = filters.BooleanFilter(method=top_rated_filter)


    class Meta:
        model = Product
        fields = {
            'id': ('exact',),
            'name': BASE_FIELD_FILTERS,
            'brand': ('exact',),
        }


class BrandShopListFilter(filters.FilterSet):

    class Meta:
        model = Brand
        fields = {
            'id': ('exact',),
            'name': BASE_FIELD_FILTERS,
        }
