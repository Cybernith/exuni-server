from rest_framework import generics
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from products.models import Product
from products.shop.filters import ShopProductSimpleFilter
from shop.exuni_admin.srializers import AdminProductsListSerializers
from store_handle.serializers import StoreHandlingProductsListSerializers


class NoPackingHandleProductSimpleListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = AdminProductsListSerializers
    filterset_class = ShopProductSimpleFilter
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return Product.objects.filter(packing_handle_done=False, product_type__in=[Product.SIMPLE, Product.VARIABLE])


class PackingHandleProductSimpleListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    serializer_class = StoreHandlingProductsListSerializers
    filterset_class = ShopProductSimpleFilter
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return Product.objects.filter(packing_handle_done=True, product_type__in=[Product.SIMPLE, Product.VARIABLE])
