from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import Q, Count, Avg, Value, FloatField, Sum
from django.db.models.functions import Coalesce

from helpers.filters import BASE_FIELD_FILTERS
from products.models import Product, Brand, Category
from django_filters import rest_framework as filters
import django_filters

from shop.models import ShopOrder

from django.contrib.postgres.aggregates import StringAgg
from django.contrib.postgres.search import SearchQuery, SearchVector, SearchRank, TrigramSimilarity
from django.db.models import Value, CharField, F, Func
from django.db.models.functions import Greatest
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from products.models import Product, Brand, Category
from server.settings import FRONT_MEDIA_URL
from shop.throttles import UserSearchAutoCompleteRateThrottle, AnonSearchAutoCompleteRateThrottle

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


def get_all_descendant_ids(category):
    descendants = []
    children = Category.objects.filter(parent=category)
    for child in children:
        descendants.append(child.id)
        descendants.extend(get_all_descendant_ids(child))
    return descendants


def category_tree_filter(queryset, name, value):
    ids = [int(cat_id) for cat_id in value.split(',') if cat_id.strip()]
    category_ids = set()

    for cat_id in ids:
        try:
            category = Category.objects.get(pk=cat_id)
            category_ids.add(category.id)
            category_ids.update(get_all_descendant_ids(category))
        except Category.DoesNotExist:
            continue

    return queryset.filter(category__id__in=category_ids).distinct()


def top_viewed_filter(queryset, name, value):
    order_by = '-view_count' if value else 'view_count'
    return queryset.order_out_of_stock_inventory_last(
    ).annotate(view_count=Count('views_log')).order_by(order_by, '-id')


def top_rated_filter(queryset, name, value):
    order_by = '-avg_rate' if value else 'avg_rate'
    return queryset.annotate(avg_rate=Coalesce(
        Avg('products_rates__level'), Value(0.0), output_field=FloatField())
    ).order_by(order_by)


def product_comments_global_search(queryset, name, value):
    return queryset.prefetch_related('product_comments').annotate(
        similarity=TrigramSimilarity('product_comments__text', value)
    ).filter(Q(similarity__gt=0.3) | Q(name__contains=value)).distinct().order_by('-similarity')


def top_selling_filter(queryset, name, value):
    return queryset.filter(id__in=[1748, 2166,  2092, 1934, 1584,  2482, 1550])


def search_value_filter(queryset, name, value):
    # if value:
    #    query = value
    #    query_value = Value(query, output_field=CharField())
    #    search_query = SearchQuery(query)
    #
    #    product_queryset = queryset.annotate(
    #        category_names=StringAgg('category__name', delimiter=' ', distinct=True),
    #        search_vector=(
    #                SearchVector('name', weight='A') +
    #                SearchVector('sixteen_digit_code', weight='B') +
    #                SearchVector('brand__name', weight='B') +
    #                SearchVector('category_names', weight='B')
    #        ),
    #        rank=SearchRank(F('search_vector'), search_query),
    #        trigram_name=TrigramSimilarity('name', query_value),
    #        trigram_sixteen_digit_code=TrigramSimilarity('sixteen_digit_code', query_value),
    #        trigram_brand=TrigramSimilarity('brand__name', query_value),
    #        trigram_category=TrigramSimilarity('category_names', query_value),
    #    ).annotate(
    #        similarity=Greatest(
    #            F('trigram_name') * 2,
    #            F('trigram_sixteen_digit_code') * 2,
    #            F('trigram_brand'),
    #            F('trigram_category')
    #        )
    #    ).filter(
    #        similarity__gt=0.1
    #    ).annotate(
    #        relevance=F('rank') + F('similarity')
    #    ).order_by('-relevance', '-similarity', '-rank')
    #
    #    return product_queryset
    #else:
    #    return queryset
    if value:
        return queryset.filter(
            Q(name__icontains=value) |
            Q(brand__name__icontains=value) |
            Q(sixteen_digit_code__icontains=value) |
            Q(explanation__icontains=value) |
            Q(summary_explanation__icontains=value)
        ).distinct()
    else:
        return queryset


class ShopProductSimpleFilter(filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    min_inventory = django_filters.NumberFilter(field_name='current_inventory__inventory', lookup_expr='gte')
    max_inventory = django_filters.NumberFilter(field_name='current_inventory__inventory', lookup_expr='lte')
    brand_in = filters.BaseInFilter(
        field_name='brand__id',
        lookup_expr='in'
    )
    currency_in = filters.BaseInFilter(
        field_name='currency__id',
        lookup_expr='in'
    )
    category_in = filters.BaseInFilter(
        field_name='category__id',
        lookup_expr='in'
    )
    category_tree = filters.CharFilter(method=category_tree_filter)
    top_viewed = filters.BooleanFilter(method=top_viewed_filter)
    top_rated = filters.BooleanFilter(method=top_rated_filter)
    top_selling = filters.BooleanFilter(method=top_selling_filter)
    global_search = filters.CharFilter(method=product_comments_global_search)
    search_value = filters.CharFilter(method=search_value_filter)

    class Meta:
        model = Product
        fields = {
            'id': ('exact',),
            'name': BASE_FIELD_FILTERS,
            'brand': ('exact',),
            'currency': ('exact',),
        }


class ShopProductWithCommentsFilter(filters.FilterSet):
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
