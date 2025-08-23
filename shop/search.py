from django.contrib.postgres.aggregates import StringAgg
from django.contrib.postgres.search import SearchQuery, SearchVector, SearchRank, TrigramSimilarity
from django.db.models import Value, CharField, F, Func, Case, When, FloatField, Sum
from django.db.models.functions import Greatest, Coalesce
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from products.models import Product, Brand, Category
from server.settings import FRONT_MEDIA_URL
from shop.api_serializers import ApiProductsListSerializers
from shop.throttles import UserSearchAutoCompleteRateThrottle, AnonSearchAutoCompleteRateThrottle


class GlobalAutoCompleteSearchAPIView(APIView):
    throttle_classes = [UserSearchAutoCompleteRateThrottle, AnonSearchAutoCompleteRateThrottle]

    def get(self, request):
        query = (request.query_params.get('search_value') or '').strip()
        if len(query) < 2:
            return Response({'result': []}, status=status.HTTP_400_BAD_REQUEST)

        tokens = [t for t in query.split() if t]
        if not tokens:
            return Response({'result': []}, status=status.HTTP_400_BAD_REQUEST)

        search_query = None
        for tok in tokens:
            q = SearchQuery(tok, search_type='plain')
            search_query = q if search_query is None else (search_query & q)

        products = Product.objects.exclude(product_type=Product.VARIATION).filter(status=Product.PUBLISHED)

        products = products.annotate(
            stock=Case(
                When(product_type=Product.SIMPLE, then=Coalesce(F('store_inventory__inventory'), 0)),
                When(product_type=Product.VARIABLE, then=Coalesce(Sum('variations__store_inventory__inventory'), 0)),
                default=Value(0),
                output_field=FloatField()
            )
        ).exclude(stock__lt=1)

        products = products.annotate(
            category_names=Coalesce(
                StringAgg('category__name', delimiter=' ', distinct=True),
                Value('', output_field=CharField())
            ),
            search_vector=(
                SearchVector('name', weight='A') +
                SearchVector('sixteen_digit_code', weight='B') +
                SearchVector('variations__sixteen_digit_code', weight='B') +
                SearchVector('brand__name', weight='B') +
                SearchVector('category_names', weight='B')
            )
        )

        primary_qs = products.annotate(
            rank=SearchRank(F('search_vector'), search_query)
        ).filter(
            search_vector=search_query
        ).annotate(
            trigram_name=TrigramSimilarity('name', query),
            trigram_code=TrigramSimilarity('sixteen_digit_code', query),
            trigram_var_code=TrigramSimilarity('variations__sixteen_digit_code', query),
            trigram_brand=TrigramSimilarity('brand__name', query),
            trigram_category=TrigramSimilarity('category_names', query),
        ).annotate(
            similarity=Greatest(
                F('trigram_name') * 2,
                F('trigram_code') * 2,
                F('trigram_var_code') * 2,
                F('trigram_brand'),
                F('trigram_category'),
                output_field=FloatField()
            ),
            relevance=F('rank') + Coalesce(F('similarity'), Value(0.0, output_field=FloatField()))
        ).annotate(
            type=Value('product', output_field=CharField()),
            picture_url=Func(Value(FRONT_MEDIA_URL), F('picture'), function='CONCAT', output_field=CharField())
        ).values('id', 'name', 'type', 'picture_url', 'relevance').order_by('-relevance', '-similarity', '-rank')[:15]

        results = list(primary_qs)

        MAX_RESULTS = 15
        if len(results) < MAX_RESULTS:
            existing_ids = {r['id'] for r in results}
            trigram_qs = products.annotate(
                trigram_name=TrigramSimilarity('name', query),
                trigram_code=TrigramSimilarity('sixteen_digit_code', query),
                trigram_var_code=TrigramSimilarity('variations__sixteen_digit_code', query),
                trigram_brand=TrigramSimilarity('brand__name', query),
                trigram_category=TrigramSimilarity('category_names', query),
            ).annotate(
                similarity=Greatest(
                    F('trigram_name') * 2,
                    F('trigram_code') * 2,
                    F('trigram_var_code') * 2,
                    F('trigram_brand'),
                    F('trigram_category'),
                    output_field=FloatField()
                )
            ).filter(
                similarity__gt=0.2
            ).exclude(id__in=existing_ids).annotate(
                type=Value('product', output_field=CharField()),
                picture_url=Func(Value(FRONT_MEDIA_URL), F('picture'), function='CONCAT', output_field=CharField())
            ).values('id', 'name', 'type', 'picture_url', 'similarity').order_by('-similarity')[:(MAX_RESULTS - len(results))]

            results.extend(list(trigram_qs.distinct()))

        brand_qs = Brand.objects.annotate(similarity=TrigramSimilarity('name', query)).filter(similarity__gt=0.3).annotate(
            type=Value('brand', output_field=CharField()),
            picture_url=Func(Value(FRONT_MEDIA_URL), F('logo'), function='CONCAT', output_field=CharField())
        ).values('id', 'name', 'type', 'picture_url').order_by('-similarity')[:5]

        category_qs = Category.objects.annotate(similarity=TrigramSimilarity('name', query)).filter(similarity__gt=0.3).annotate(
            type=Value('category', output_field=CharField())
        ).values('id', 'name', 'type').order_by('-similarity').distinct()[:5]

        final_result = []
        final_result.extend(results)
        final_result.extend(list(brand_qs))
        final_result.extend(list(category_qs))

        return Response({'result': final_result}, status=status.HTTP_200_OK)


class GlobalSearchAPIView(APIView):
    throttle_classes = [UserSearchAutoCompleteRateThrottle, AnonSearchAutoCompleteRateThrottle]

    def get(self, request):
        query = request.query_params.get('search_value', '').strip()
        query_value = Value(query, output_field=CharField())
        search_query = SearchQuery(query)

        product_queryset = Product.objects.annotate(
            category_names=StringAgg('category__name', delimiter=' ', distinct=True),
            search_vector=(
                    SearchVector('name', weight='A') +
                    SearchVector('sixteen_digit_code', weight='B') +
                    SearchVector('brand__name', weight='B') +
                    SearchVector('category_names', weight='B')
            ),
            rank=SearchRank(F('search_vector'), search_query),
            trigram_name=TrigramSimilarity('name', query_value),
            trigram_sixteen_digit_code=TrigramSimilarity('sixteen_digit_code', query_value),
            trigram_brand=TrigramSimilarity('brand__name', query_value),
            trigram_category=TrigramSimilarity('category_names', query_value),
        ).annotate(
            similarity=Greatest(
                F('trigram_name') * 2,
                F('trigram_sixteen_digit_code') * 2,
                F('trigram_brand'),
                F('trigram_category')
            )
        ).filter(
            similarity__gt=0.1
        ).annotate(
            relevance=F('rank') + F('similarity')
        ).order_by('-relevance', '-similarity', '-rank').select_related('brand').prefetch_related('variations')

        return Response(ApiProductsListSerializers(product_queryset, many=True).data, status=status.HTTP_200_OK)

