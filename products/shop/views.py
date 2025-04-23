from rest_framework import generics
from rest_framework.pagination import LimitOffsetPagination

from products.models import Product
from products.shop.filters import ShopProductFilter
from products.shop.serializers import ShopProductsListSerializers


class ProductListView(generics.ListAPIView):

    serializer_class = ShopProductsListSerializers
    filterset_class = ShopProductFilter
    ordering_fields = '__all__'
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return Product.objects.select_related('brand', 'category', 'current_price', 'current_inventory',)

