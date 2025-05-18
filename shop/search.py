from django.contrib.postgres.aggregates import StringAgg
from django.contrib.postgres.search import SearchQuery, SearchVector, SearchRank, TrigramSimilarity
from django.db.models import Value, CharField, F
from django.db.models.functions import Greatest
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from products.models import Product, Brand, Category
from shop.throttles import UserSearchAutoCompleteRateThrottle, AnonSearchAutoCompleteRateThrottle


class GlobalAutoCompleteSearchAPIView(APIView):
    throttle_classes = [UserSearchAutoCompleteRateThrottle, AnonSearchAutoCompleteRateThrottle]

    def get(self, request):
        query = request.query_params.get('search_value', '').strip()
        if len(query) < 3:
            return Response({'result': []}, status=status.HTTP_400_BAD_REQUEST)

        result = []

        query_value = Value(query, output_field=CharField())
        search_query = SearchQuery(query)

        product_queryset = Product.objects.annotate(
            category_names=StringAgg('category__name', delimiter=' ', distinct=True),
            search_vector=(
                    SearchVector('name', weight='A') +
                    SearchVector('brand__name', weight='B') +
                    SearchVector('category_names', weight='B')
            ),
            rank=SearchRank(F('search_vector'), search_query),
            trigram_name=TrigramSimilarity('name', query_value),
            trigram_brand=TrigramSimilarity('brand__name', query_value),
            trigram_category=TrigramSimilarity('category_names', query_value),
        ).annotate(
            similarity=Greatest(
                F('trigram_name') * 2,
                F('trigram_brand'),
                F('trigram_category')
            )
        ).filter(
            similarity__gt=0.1
        ).annotate(
            relevance=F('rank') + F('similarity')
        ).annotate(
            type=Value('product', output_field=CharField())
        ).values(
            'id', 'name', 'type'
        ).order_by('-relevance', '-similarity', '-rank')[:5]

        result.extend(product_queryset)

        brand_queryset = Brand.objects.annotate(
            similarity=TrigramSimilarity('name', query_value)
        ).filter(
            similarity__gt=0.3
        ).annotate(
            type=Value('brand', output_field=CharField())
        ).values(
            'id', 'name', 'type'
        ).order_by('-similarity')[:5]

        result.extend(brand_queryset)

        category_queryset = Category.objects.annotate(
            similarity=TrigramSimilarity('name', query_value)
        ).filter(
            similarity__gt=0.3
        ).annotate(
            type=Value('category', output_field=CharField())
        ).values(
            'id', 'name', 'type'
        ).order_by('-similarity').distinct()[:5]

        result.extend(category_queryset)

        return Response({'result': result}, status=status.HTTP_200_OK)
