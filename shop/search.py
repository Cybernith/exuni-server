from django.contrib.postgres.aggregates import StringAgg
from django.contrib.postgres.search import SearchQuery, SearchVector, SearchRank, TrigramSimilarity
from django.db.models import Q, Value, CharField
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

        search_query = SearchQuery(query)
        search_vector = (
            SearchVector('name', weight='A') +
            SearchVector('brand__name', weight='B') +
            SearchVector('category__name', weight='B')

        )
        result = []

        product_queryset = Product.objects.annotate(
            category_names=StringAgg('category__name', delimiter=' ', distinct=True),
            rank=SearchRank(search_vector, search_query),
            similarity=Greatest(
                TrigramSimilarity('name', query),
                TrigramSimilarity('brand__name', query),
                TrigramSimilarity('category_names', query),
            )
        ).filter(
            similarity__gt=0.15
        ).annotate(
            type=Value('product', output_field=CharField())
        ).values(
            'id', 'name', 'type'
        ).order_by(
            '-rank',
            '-similarity'
        )[:5]

        result.extend(product_queryset)

        brand_queryset = Brand.objects.annotate(
            similarity=TrigramSimilarity('name', query)
        ).filter(
            similarity__gt=0.3
        ).annotate(
            type=Value('brand', output_field=CharField())
        ).values(
            'id', 'name', 'type'
        ).order_by(
            '-similarity'
        )[:5]

        result.extend(brand_queryset)

        category_queryset = Category.objects.annotate(
            similarity=TrigramSimilarity('name', query)
        ).filter(
            similarity__gt=0.3
        ).annotate(
            type=Value('category', output_field=CharField())
        ).values('id', 'name', 'type').order_by('-similarity').distinct()[:5]

        result.extend(category_queryset)

        return Response({'result': result}, status=status.HTTP_200_OK)
