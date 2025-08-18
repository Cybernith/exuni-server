from django.db.models.functions import Coalesce
from rest_framework import generics
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from products.models import Product
from products.shop.filters import ShopProductSimpleFilter
from server.store_configs import PACKING_STORE_ID
from shop.exuni_admin.srializers import AdminProductsListSerializers
from store_handle.lists.filters import ProductStoreInventorySimpleFilter
from store_handle.models import ProductStoreInventory
from store_handle.serializers import StoreHandlingProductsListSerializers, HandleDoneProductsListSerializers, \
    ProductStoreInventoryListSerializers
from django.db.models import Case, When, BooleanField, Value, F, Sum, Q


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


class StoreHandleProductSimpleListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    serializer_class = HandleDoneProductsListSerializers
    filterset_class = ShopProductSimpleFilter
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return Product.objects.filter(store_handle_done=True, product_type__in=[Product.SIMPLE, Product.VARIATION])


class WaitForStoreHandleProductSimpleListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    serializer_class = StoreHandlingProductsListSerializers
    filterset_class = ShopProductSimpleFilter
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return Product.objects.filter(store_handle_done=False, product_type__in=[Product.SIMPLE, Product.VARIATION])


class StoreInventoryListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    serializer_class = ProductStoreInventoryListSerializers
    filterset_class = ProductStoreInventorySimpleFilter
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return ProductStoreInventory.objects.filter(
            product__product_type__in=[Product.SIMPLE, Product.VARIATION]).annotate(
            total_inventory=Sum('product__store_inventory__inventory',
                                filter=~Q(product__store_inventory__store_id=PACKING_STORE_ID))
        ).annotate(
            total_inventory=Coalesce(
                Sum('product__store_inventory__inventory',
                    filter=~Q(product__store_inventory__store_id=PACKING_STORE_ID)), 0
            ),
            inventory_value=Coalesce('inventory', 0),
            minimum_inventory_value=Coalesce('minimum_inventory', 0),
        ).annotate(
            is_minimum=Case(
                When(minimum_inventory_value__gt=F('inventory_value'), total_inventory__gt=0, then=Value(True)),
                default=Value(False),
                output_field=BooleanField()
            )
        ).order_by('is_minimum')
