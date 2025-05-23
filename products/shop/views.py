from PIL import Image
from django.core.cache import cache
from django.db.models import Q, Count, F, Prefetch
from django.shortcuts import get_object_or_404
from rest_framework import generics, status, viewsets
from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie

from crm.functions import save_product_view_log, get_recommended_products
from helpers.functions import get_current_user
from products.lists.filters import RootCategoryFilter
from products.models import Product, Category, Brand
from products.shop.filters import ShopProductFilter, BrandShopListFilter, ShopProductSimpleFilter
from products.shop.serializers import ShopProductsListSerializers, ShopCommentSerializer, \
    ShopProductRateSerializer, RootCategorySerializer
from products.trottles import UserProductDetailRateThrottle, AnonProductDetailRateThrottle, AnonProductListRateThrottle, \
    UserProductListRateThrottle, CreateCommentRateThrottle, RateUpsertRateThrottle, CategoryTreeThrottle, BrandThrottle, \
    RootCategoryThrottle
from products.utils import ImageFeatureExtractor
from shop.api_serializers import ApiProductsListSerializers, ApiProductDetailSerializers, ApiBrandListSerializer, \
    ApiProductsWithCommentsListSerializers, ApiUserCommentProductsSimpleListSerializers
from shop.models import Comment
from shop.serializers import CommentRepliesSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

from rest_framework.parsers import MultiPartParser, FormParser
import numpy as np


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
    serializer_class = ApiProductsListSerializers
    throttle_classes = [UserProductListRateThrottle, AnonProductListRateThrottle]
    filterset_class = ShopProductSimpleFilter
    ordering_fields = '__all__'
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return Product.objects.filter(status=Product.PUBLISHED, product_type__in=[Product.VARIABLE, Product.SIMPLE])


class ShopProductWithCommentsListView(generics.ListAPIView):
    serializer_class = ApiProductsWithCommentsListSerializers
    throttle_classes = [UserProductListRateThrottle, AnonProductListRateThrottle]
    filterset_class = ShopProductSimpleFilter
    ordering_fields = '__all__'
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return Product.objects.filter(
            status=Product.PUBLISHED,
            product_type__in=[Product.VARIABLE, Product.SIMPLE]
        ).annotate(
            confirmed_comment_count=Count('product_comments', filter=Q(product_comments__confirmed=True))
        ).filter(
            confirmed_comment_count__gt=0
        ).prefetch_related(
            Prefetch(
                'product_comments',
                queryset=Comment.objects.filter(confirmed=True)
            )
        )


class ShopProductDetailView(generics.RetrieveAPIView):
    serializer_class = ApiProductDetailSerializers
    throttle_classes = [UserProductDetailRateThrottle, AnonProductDetailRateThrottle]
    lookup_field = 'id'

    queryset = Product.objects.annotate(view_count=Count('views_log'))

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
    serializer_class = ApiProductsListSerializers
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

        properties_ids = product.properties.all().values_list('id', flat=True)
        avails_ids = product.avails.all().values_list('id', flat=True)

        related_products = Product.objects.annotate(view_count=Count('views_log')).filter(
            Q(category__in=product.category.all()) |
            Q(avails__id__in=avails_ids) |
            Q(properties__id__in=properties_ids) |
            Q(brand=product.brand)
        ).exclude(id=product_id).annotate(
            related_properties=Count('properties', filter=Q(properties__id__in=properties_ids)),
            related_avails=Count('avails', filter=Q(avails__id__in=avails_ids)),
            similarity_score=F('related_properties') + F('related_avails')
        ).order_by('-similarity_score').distinct().select_related('brand').prefetch_related('properties', 'avails')
        cache.set(cache_key, related_products, 60 * 10)
        return related_products


class SimilarBrandProductsApiView(generics.ListAPIView):
    serializer_class = ApiProductsListSerializers
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

        cache.set(cache_key, similar_brand_products, 60 * 10)
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

        cache.set(cache_key, similar_avails_products, 60 * 10)
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

        cache.set(cache_key, similar_properties_products, 60 * 10)
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

        cache.set(cache_key, similar_category_products, 60 * 10)
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
    permission_classes = [AllowAny]
    throttle_classes = [BrandThrottle]
    CACHE_KEY = 'brands_data'
    CACHE_TIMEOUT = 60 * 60 * 6

    serializer_class = ApiBrandListSerializer
    filterset_class = BrandShopListFilter
    ordering_fields = '__all__'
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        brands = cache.get(self.CACHE_KEY)

        if not brands:
            brands = Brand.objects.all()
            cache.set(self.CACHE_KEY, brands, self.CACHE_TIMEOUT)

        return brands


class CurrentUserHasOrderProductViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ApiProductsListSerializers

    def get_queryset(self):
        user = get_current_user()
        return Product.objects.filter(shop_order_items__shop_order__customer=user).distinct()


class CurrentUserRelatedProductViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ApiProductsListSerializers
    pagination_class = None
    permission_classes = [IsAuthenticated]
    CACHE_TIMEOUT = 60

    @method_decorator(cache_page(CACHE_TIMEOUT))
    @method_decorator(vary_on_cookie)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        return Product.objects.filter(
            id__in=get_recommended_products(
                user=get_current_user(),
                limit=10
            )
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class PendingReviewProductsView(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ApiProductsListSerializers

    def get_queryset(self):
        user = get_current_user()
        return Product.objects.filter(shop_order_items__shop_order__customer=user).exclude(
            product_comments__customer=user
        ).distinct()


class UserProductsWithCommentView(viewsets.ReadOnlyModelViewSet):
    serializer_class = ApiUserCommentProductsSimpleListSerializers

    def get_queryset(self):
        user = get_current_user()
        return Product.objects.filter(
            Q(shop_order_items__shop_order__customer=user) & Q(product_comments__customer=user)).distinct()


extractor = ImageFeatureExtractor()


class ImageSearchAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        uploaded_file = request.FILES.get('image')
        if not uploaded_file:
            return Response({'error': 'هیچ تصویری آپلود نشده است'}, status=400)

        try:
            img = Image.open(uploaded_file).convert('RGB')
            query_features = extractor.extract_features(img)

            products = Product.objects.exclude(feature_vector=None)
            if not products.exists():
                return Response({'error': 'هیچ محصولی یافت نشد'}, status=404)

            feature_vectors = np.array([np.frombuffer(p.feature_vector, dtype=np.float32) for p in products])
            query_features = query_features.flatten()
            norms = np.linalg.norm(feature_vectors, axis=1) * np.linalg.norm(query_features)
            similarities = np.dot(feature_vectors, query_features) / norms
            similarities = np.nan_to_num(similarities, nan=0.0)

            top_indices = np.argsort(similarities)[::-1][:5]
            top_products = [products[i] for i in top_indices]

            serializer = ApiProductsListSerializers(top_products, many=True)
            return Response(serializer.data)

        except Exception as e:
            return Response({'error': f'خطا در پردازش: {str(e)}'}, status=500)
