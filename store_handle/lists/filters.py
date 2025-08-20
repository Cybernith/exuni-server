from django.db.models import Q
from django.db.models.functions import Cast

from django_filters import rest_framework as filters
from django.contrib.postgres.search import SearchQuery, SearchVector, SearchRank

from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import Value, CharField, F

from server.store_configs import PACKING_STORE_ID
from store_handle.models import ProductStoreInventory


def id_in_filter(queryset, name, value):
    if not value:
        return queryset
    search_terms = str(value)
    return queryset.annotate(id_str=Cast('id', output_field=CharField())).filter(
        product__id_str__icontains=search_terms)


def sku_filter(queryset, name, value):
    if not value:
        return queryset
    sku = str(value)
    result = queryset.filter(
        Q(product__sixteen_digit_code__iendswith=sku) | Q(product__variations__sixteen_digit_code__iendswith=sku)
    ).distinct()
    if not result.count() > 0:
        result = queryset.filter(
            Q(product__sixteen_digit_code__icontains=sku) | Q(product__variations__sixteen_digit_code__icontains=sku)
        ).distinct()
    return result


def name_search_products(queryset, name, value):
    if not value:
        return queryset

    query = value
    query_value = Value(query, output_field=CharField())
    search_query = SearchQuery(query)

    product_queryset = queryset.annotate(
        search_vector=(
            SearchVector('product__name', weight='A')
        ),
        rank=SearchRank(F('search_vector'), search_query),
        trigram_name=TrigramSimilarity('product__name', query_value),
    ).filter(
        trigram_name__gt=0.2
    ).annotate(
        relevance=F('rank') + F('trigram_name')
    ).order_by(
        '-relevance', '-trigram_name', '-rank'
    )
    return product_queryset.distinct()


def inventory_store_filter(queryset, name, value):
    if not value:
        return queryset
    return queryset.filter(
        product__store_inventory__store_id=value,
        product__store_inventory__inventory__gt=0,
        store_id=PACKING_STORE_ID
    ).distinct()

class ProductStoreInventorySimpleFilter(filters.FilterSet):
    name_search = filters.CharFilter(method=name_search_products)
    id_in = filters.NumberFilter(method=id_in_filter)
    inventory_store = filters.NumberFilter(method=inventory_store_filter)
    sku = filters.CharFilter(method=sku_filter)
    brand_in = filters.BaseInFilter(
        field_name='product__brand__id',
        lookup_expr='in'
    )

    class Meta:
        model = ProductStoreInventory
        fields = {
            'id': ('exact',),
            'store': ('exact',),
            'product': ('exact',),
        }
