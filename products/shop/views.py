from rest_framework import generics
from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination
from rest_framework.permissions import IsAuthenticated

from products.models import Product
from products.shop.filters import ShopProductFilter
from products.shop.serializers import ShopProductsListSerializers, ShopProductDetailSerializers, ShopCommentSerializer, \
    ShopProductRateSerializer
from shop.models import Comment
from shop.serializers import CommentRepliesSerializer


class ShopProductListView(generics.ListAPIView):

    serializer_class = ShopProductsListSerializers
    filterset_class = ShopProductFilter
    ordering_fields = '__all__'
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return Product.objects.filter(status=Product.PUBLISHED).select_related(
            'brand', 'category', 'current_price', 'current_inventory', 'products_in_wish_list', 'product_comments'
        ).prefetch_related('properties', 'avails')


class ShopProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.select_related(
        'brand',
        'category',
        'current_price',
        'current_inventory',
        'products_in_wish_list',
        'product_comments'
        'gallery'
    ).prefetch_related(
        'properties',
        'avails'
    )
    serializer_class = ShopProductDetailSerializers
    lookup_field = 'id'


class CommentCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ShopCommentSerializer
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
    serializer_class = ShopProductRateSerializer

