from rest_framework import generics
from rest_framework.pagination import LimitOffsetPagination

from products.models import Product
from products.shop.filters import ShopProductFilter
from products.shop.serializers import ShopProductsListSerializers, ShopProductDetailSerializers


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


