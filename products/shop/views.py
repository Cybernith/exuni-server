from django.core.cache import cache
from django.db.models import Q, Count, F
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from crm.functions import save_product_view_log
from products.lists.filters import RootCategoryFilter
from products.models import Product, Category, Brand
from products.serializers import BrandShopListSerializer, CategorySerializer
from products.shop.filters import ShopProductFilter, BrandShopListFilter, ShopProductSimpleFilter
from products.shop.serializers import ShopProductsListSerializers, ShopProductDetailSerializers, ShopCommentSerializer, \
    ShopProductRateSerializer, ShopProductsSimpleListSerializers, RootCategorySerializer
from products.trottles import UserProductDetailRateThrottle, AnonProductDetailRateThrottle, AnonProductListRateThrottle, \
    UserProductListRateThrottle, CreateCommentRateThrottle, RateUpsertRateThrottle, CategoryTreeThrottle, BrandThrottle, \
    RootCategoryThrottle
from shop.models import Comment
from shop.serializers import CommentRepliesSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter


class ShopProductListView(generics.ListAPIView):

    serializer_class = ShopProductsListSerializers
    throttle_classes = [UserProductListRateThrottle, AnonProductListRateThrottle]
    filterset_class = ShopProductFilter
    ordering_fields = '__all__'
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return Product.objects.filter(status=Product.PUBLISHED).annotate(view_count=Count('views_log')).select_related(
            'brand', 'category', 'current_price', 'current_inventory', 'products_in_wish_list', 'product_comments'
        ).prefetch_related('properties', 'avails')


class ShopProductSimpleListView(generics.ListAPIView):

    serializer_class = ShopProductsSimpleListSerializers
    throttle_classes = [UserProductListRateThrottle, AnonProductListRateThrottle]
    filterset_class = ShopProductSimpleFilter
    ordering_fields = '__all__'
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return Product.objects.filter(status=Product.PUBLISHED, product_type__in=[Product.VARIABLE, Product.SIMPLE])


class ShopProductDetailView(generics.RetrieveAPIView):
    serializer_class = ShopProductDetailSerializers
    throttle_classes = [UserProductDetailRateThrottle, AnonProductDetailRateThrottle]
    lookup_field = 'id'

    queryset = Product.objects.annotate(view_count=Count('views_log')).select_related(
        'brand',
        'category',
        'current_price',
        'current_inventory',
        'products_in_wish_list',
        # 'product_comments'
        'gallery'
    ).prefetch_related(
        'properties',
        'avails'
    )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        save_product_view_log(request=request, product=instance)
        return Response(serializer.data)


class CommentCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ShopCommentSerializer
    throttle_classes = [CreateCommentRateThrottle]

    queryset = Comment.objects.all()


class CommentPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 20


class ShopProductCommentListView(generics.ListAPIView):
    serializer_class = CommentRepliesSerializer
    pagination_class = CommentPagination

    def get_queryset(self):
        product_id = self.kwargs.get('id')
        return Comment.objects.filter(
            product__id=product_id, reply__isnull=True
        ).prefetch_related('replies').select_related('customer')


class RateUpsertApiView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [RateUpsertRateThrottle]
    serializer_class = ShopProductRateSerializer


class RelatedProductPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 50


class RelatedProductsApiView(generics.ListAPIView):
    serializer_class = ShopProductsListSerializers
    throttle_classes = [UserProductListRateThrottle, AnonProductListRateThrottle]
    pagination_class = RelatedProductPagination

    def get_queryset(self):
        product_id = self.kwargs.get('product_id')
        cache_key = f'related_products_{product_id}'
        cache_queryset = cache.get(cache_key)

        if cache_queryset:
            return cache_queryset

        try:
            product = Product.objects.prefetch_related('properties', 'avails').get(id=product_id)
        except Product.DoesNotExist:
            return Product.objects.none()

        properties_ids = product.properties.values_list('id', flat=True)
        avails_ids = product.avails.values_list('id', flat=True)

        related_products = Product.objects.annotate(view_count=Count('views_log')).filter(
            Q(category=product.category) |
            Q(avails__id__in=avails_ids) |
            Q(properties__id__in=properties_ids) |
            Q(brand=product.brand)
        ).exclude(id=product_id).annotate(
            related_properties=Count('properties', filter=Q(properties__id__in=properties_ids)),
            related_avails=Count('avails', filter=Q(avails__id__in=avails_ids)),
            similarity_score=F('related_properties') + F('related_avails')
        ).order_by('-similarity_score').distinct().select_related(
            'category', 'brand'
        ).prefetch_related(
            'properties', 'avails'
        )
        cache.set(cache_key, related_products, 60*10)
        return related_products


class SimilarBrandProductsApiView(generics.ListAPIView):
    serializer_class = ShopProductsListSerializers
    throttle_classes = [UserProductListRateThrottle, AnonProductListRateThrottle]
    pagination_class = RelatedProductPagination

    def get_queryset(self):
        product_id = self.kwargs.get('product_id')
        cache_key = f'similar_brand_products_{product_id}'
        cache_queryset = cache.get(cache_key)

        if cache_queryset:
            return cache_queryset

        product = get_object_or_404(Product, pk=product_id)
        similar_brand_products = Product.objects.filter(
            Q(status=Product.PUBLISHED) & Q(brand=product.brand)
        ).exclude(id=product_id).annotate(view_count=Count('views_log')).select_related(
            'brand', 'category', 'current_price', 'current_inventory', 'products_in_wish_list', 'product_comments'
        ).prefetch_related('properties', 'avails')

        cache.set(cache_key, similar_brand_products, 60*10)
        return similar_brand_products


class SimilarAvailProductsApiView(generics.ListAPIView):
    serializer_class = ShopProductsListSerializers
    throttle_classes = [UserProductListRateThrottle, AnonProductListRateThrottle]
    pagination_class = RelatedProductPagination

    def get_queryset(self):
        product_id = self.kwargs.get('product_id')
        cache_key = f'similar_avail_products_{product_id}'
        cache_queryset = cache.get(cache_key)

        if cache_queryset:
            return cache_queryset

        product = get_object_or_404(Product, pk=product_id)
        similar_avails_products = Product.objects.filter(
            Q(status=Product.PUBLISHED) & Q(avails__in=product.avails)
        ).exclude(id=product_id).annotate(view_count=Count('views_log')).select_related(
            'brand', 'category', 'current_price', 'current_inventory', 'products_in_wish_list', 'product_comments'
        ).prefetch_related('properties', 'avails')

        cache.set(cache_key, similar_avails_products, 60*10)
        return similar_avails_products


class SimilarPropertiesProductsApiView(generics.ListAPIView):
    serializer_class = ShopProductsListSerializers
    throttle_classes = [UserProductListRateThrottle, AnonProductListRateThrottle]
    pagination_class = RelatedProductPagination

    def get_queryset(self):
        product_id = self.kwargs.get('product_id')
        cache_key = f'similar_property_products_{product_id}'
        cache_queryset = cache.get(cache_key)

        if cache_queryset:
            return cache_queryset

        product = get_object_or_404(Product, pk=product_id)
        similar_properties_products = Product.objects.filter(
            Q(status=Product.PUBLISHED) & Q(properties__in=product.properties)
        ).exclude(id=product_id).annotate(view_count=Count('views_log')).select_related(
            'brand', 'category', 'current_price', 'current_inventory', 'products_in_wish_list', 'product_comments'
        ).prefetch_related('properties', 'avails')

        cache.set(cache_key, similar_properties_products, 60*10)
        return similar_properties_products


class SimilarCategoryProductsApiView(generics.ListAPIView):
    serializer_class = ShopProductsListSerializers
    throttle_classes = [UserProductListRateThrottle, AnonProductListRateThrottle]
    pagination_class = RelatedProductPagination

    def get_queryset(self):
        product_id = self.kwargs.get('product_id')
        cache_key = f'similar_category_products_{product_id}'
        cache_queryset = cache.get(cache_key)

        if cache_queryset:
            return cache_queryset

        product = get_object_or_404(Product, pk=product_id)
        similar_category_products = Product.objects.filter(
            Q(status=Product.PUBLISHED) & Q(category=product.category)
        ).exclude(id=product_id).annotate(view_count=Count('views_log')).select_related(
            'brand', 'category', 'current_price', 'current_inventory', 'products_in_wish_list', 'product_comments'
        ).prefetch_related('properties', 'avails')

        cache.set(cache_key, similar_category_products, 60*10)
        return similar_category_products


class TopViewedShopProductsAPIView(generics.ListAPIView):
    serializer_class = ShopProductsListSerializers
    throttle_classes = [UserProductListRateThrottle, AnonProductListRateThrottle]
    pagination_class = RelatedProductPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['brand', 'category']
    ordering_fields = ['view_count', 'current_price', 'title']
    ordering = ['-view_count']

    def get_queryset(self):
        return (
            Product.objects
            .prefetch_related('brand', 'category')
            .select_related(
                'brand', 'category', 'current_price', 'current_inventory', 'products_in_wish_list', 'product_comments'
            )
            .annotate(view_count=Count('views_log'))
            .order_by('-view_count', '-id')
        )


class RootCategoryListView(generics.ListAPIView):
    throttle_classes = [RootCategoryThrottle]
    CACHE_KEY = 'root_category_data'
    CACHE_TIMEOUT = 60 * 60 * 6

    serializer_class = RootCategorySerializer
    filterset_class = RootCategoryFilter
    ordering_fields = '__all__'
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        categories = cache.get(self.CACHE_KEY)

        if not categories:
            categories = Category.objects.filter(parent=None)
            cache.set(self.CACHE_KEY, categories, self.CACHE_TIMEOUT)

        return categories


class CategoryTreeView(APIView):
    throttle_classes = [CategoryTreeThrottle]
    CACHE_KEY = 'category_tree_data'
    CACHE_TIMEOUT = 60 * 60 * 6

    def get(self, request):
        tree = cache.get(self.CACHE_KEY)

        if not tree:
            categories = Category.objects.all().only('id', 'name', 'parent_id').select_related('parent')

            category_map = {}
            for category in categories:
                category_map.setdefault(category.parent_id, []).append({
                    'id': category.id,
                    'name': category.name,
                    'children': []
                })

            def build_tree(parent_id=None):
                nodes = []
                for current_category in category_map.get(parent_id, []):
                    current_category['children'] = build_tree(current_category['id'])
                    nodes.append(current_category)
                return nodes

            tree = build_tree()

            cache.set(self.CACHE_KEY, tree, self.CACHE_TIMEOUT)

        return Response(tree, status=status.HTTP_200_OK)


class BrandShopListView(generics.ListAPIView):
    throttle_classes = [BrandThrottle]
    CACHE_KEY = 'brands_data'
    CACHE_TIMEOUT = 60 * 60 * 6

    serializer_class = BrandShopListSerializer
    filterset_class = BrandShopListFilter
    ordering_fields = '__all__'
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        brands = cache.get(self.CACHE_KEY)

        if not brands:
            brands = Brand.objects.all()
            cache.set(self.CACHE_KEY, brands, self.CACHE_TIMEOUT)

        return brands
