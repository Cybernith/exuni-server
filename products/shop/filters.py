from django.db.models import Q, Count, Avg, FloatField, Sum, When, IntegerField, OuterRef, Subquery, Case, Max, QuerySet
from django.db.models.functions import Coalesce, Cast, Greatest, Length

from helpers.filters import BASE_FIELD_FILTERS
from django_filters import rest_framework as filters
import django_filters
from django.contrib.postgres.search import SearchQuery, SearchVector, SearchRank
from django.db.models.functions import RowNumber
from django.db.models.expressions import Window


from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import Value, CharField, F

from products.models import Product, Brand, Category

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
    # Parse input category IDs
    ids = [int(cat_id) for cat_id in value.split(',') if cat_id.strip()]
    if not ids:
        return queryset.none()

    # Get valid root categories
    root_categories = Category.objects.filter(id__in=ids)
    root_ids = list(root_categories.values_list('id', flat=True))
    if not root_ids:
        return queryset.none()

    # Collect all relevant category IDs (roots + descendants)
    all_ids = set(root_ids)
    current_level_ids = set(root_ids)

    # Breadth-first traversal to get all descendants
    while current_level_ids:
        # Get direct children of current level categories
        children = Category.objects.filter(
            parent_id__in=current_level_ids
        ).exclude(id__in=all_ids).values_list('id', flat=True)

        children_ids = set(children)
        if not children_ids:
            break

        all_ids.update(children_ids)
        current_level_ids = children_ids

    # Filter the original queryset
    return queryset.filter(category__id__in=all_ids).distinct()


def category_in_filter(queryset, name, value):
    ids = [int(cat_id) for cat_id in value.split(',') if cat_id.strip()]
    if not ids:
        return queryset.none()

    return queryset.filter(category__id__in=ids).distinct()


def brand_in_filter(queryset, name, value):
    ids = [int(brand_id) for brand_id in value.split(',') if brand_id.strip()]
    if not ids:
        return queryset.none()

    return queryset.filter(brand_id__in=ids).distinct()


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
    return queryset.filter(id__in=[6640, 3443, 6772, 6739, 3237, 2166, 6459,  2386, 1934,3831, 1584,  2482, 1550])


def search_value_filter(queryset, name, value):
    if not value:
        return queryset

    queryset = queryset.exclude(product_type=Product.VARIATION)

    query = value
    query_value = Value(query, output_field=CharField())
    search_query = SearchQuery(query)

    product_queryset = queryset.annotate(
        search_vector=(
                SearchVector('name', weight='A') +
                SearchVector('sixteen_digit_code', weight='B') +
                SearchVector('brand__name', weight='B')
        ),
        rank=SearchRank(F('search_vector'), search_query),
        trigram_name=TrigramSimilarity('name', query_value),
        trigram_sixteen_digit_code=TrigramSimilarity('sixteen_digit_code', query_value),
        trigram_brand=TrigramSimilarity('brand__name', query_value),
    ).annotate(
        similarity=Greatest(
            F('trigram_name') * 2,
            F('trigram_sixteen_digit_code') * 2,
            F('trigram_brand'),
        )
    ).annotate(
        stock=Case(
            When(
                product_type=Product.SIMPLE,
                then=F('current_inventory__inventory')
            ),
            When(
                product_type=Product.VARIABLE,
                then=Sum('variations__current_inventory__inventory')
            ),
            default=Value(0),
            output_field=FloatField()
        )
    ).filter(
        similarity__gt=0.2
    ).annotate(
        relevance=F('rank') + F('similarity')
    ).order_by(
        '-relevance', '-similarity', '-rank'
    )

    has_stock = product_queryset.exclude(stock__lt=1)
    no_stock = product_queryset.exclude(stock__gte=1)

    combined_list = list(has_stock) + list(no_stock)
    ids_in_order = [obj.pk for obj in combined_list]

    combined_qs = Product.objects.filter(
        pk__in=ids_in_order
    ).annotate(
        custom_order=Case(
            *[When(pk=pk, then=Value(i)) for i, pk in enumerate(ids_in_order)],
            output_field=IntegerField()
        )
    ).order_by('custom_order')

    return combined_qs.select_related('brand').prefetch_related('variations')


def id_in_filter(queryset, name, value):
    if not value:
        return queryset
    search_terms = str(value)
    return queryset.annotate(id_str=Cast('id', output_field=CharField())).filter(id_str__icontains=search_terms)


def sku_filter(queryset, name, value):
    if not value:
        return queryset
    sku = str(value)
    return queryset.filter(
        Q(sixteen_digit_code__icontains=sku) | Q(variations__sixteen_digit_code__icontains=sku)
    ).distinct()


def name_search_products(queryset, name, value):
    if not value:
        return queryset

    query = value
    query_value = Value(query, output_field=CharField())
    search_query = SearchQuery(query)

    product_queryset = queryset.annotate(
        search_vector=(
                SearchVector('name', weight='A')
        ),
        rank=SearchRank(F('search_vector'), search_query),
        trigram_name=TrigramSimilarity('name', query_value),
    ).filter(
        trigram_name__gt=0.2
    ).annotate(
        relevance=F('rank') + F('trigram_name')
    ).order_by(
        '-relevance', '-trigram_name', '-rank'
    )
    return product_queryset.distinct()


class ShopProductSimpleFilter(filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    max_inventory = filters.NumberFilter(method='filter_inventory')
    min_inventory = filters.NumberFilter(method='filter_inventory')
    currency_in = filters.BaseInFilter(
        field_name='currency__id',
        lookup_expr='in'
    )
    status_in = filters.BaseInFilter(
        field_name='status',
        lookup_expr='in'
    )
    category_tree = filters.CharFilter(method=category_tree_filter)
    brand_in = filters.CharFilter(method=brand_in_filter)
    category_in = filters.CharFilter(method=category_in_filter)
    top_viewed = filters.BooleanFilter(method=top_viewed_filter)
    top_rated = filters.BooleanFilter(method=top_rated_filter)
    top_selling = filters.BooleanFilter(method=top_selling_filter)
    global_search = filters.CharFilter(method=product_comments_global_search)
    search_value = filters.CharFilter(method=search_value_filter)
    name_search = filters.CharFilter(method=name_search_products)
    id_in = filters.NumberFilter(method=id_in_filter)
    sku = filters.CharFilter(method=sku_filter)

    class Meta:
        model = Product
        fields = {
            'id': ('exact',),
            'name': BASE_FIELD_FILTERS,
            'sixteen_digit_code': BASE_FIELD_FILTERS,
            'brand': ('exact',),
            'currency': ('exact',),
            'supplier': ('exact',),
        }

    def filter_inventory(self, queryset, name, value):
        # First handle simple products and variation parents
        simple_products = queryset.filter(
            Q(product_type=Product.SIMPLE) | Q(product_type=Product.VARIATION)
        ).annotate(
            total_inventory=F('current_inventory__inventory')
        )

        # Then handle products with variations
        products_with_variations = queryset.filter(
            variations__isnull=False
        ).annotate(
            total_inventory=Sum('variations__current_inventory__inventory')
        )

        # Combine both querysets (no union needed)
        combined_ids = list(simple_products.values_list('id', flat=True)) + \
                       list(products_with_variations.values_list('id', flat=True))

        # Get the final filtered queryset
        filtered_queryset = queryset.filter(id__in=combined_ids)

        if name == 'min_inventory':
            return filtered_queryset.filter(
                Q(product_type__in=[Product.SIMPLE, Product.VARIATION],
                  current_inventory__inventory__gte=value) |
                Q(variations__current_inventory__inventory__gte=value)
            ).distinct()
        elif name == 'max_inventory':
            return filtered_queryset.filter(
                Q(product_type__in=[Product.SIMPLE, Product.VARIATION],
                  current_inventory__inventory__lte=value) |
                Q(variations__current_inventory__inventory__lte=value)
            ).distinct()
        return filtered_queryset


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
