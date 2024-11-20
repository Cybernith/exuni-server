from django.db.models import Q
from rest_framework import generics
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated

from affiliate.views import get_business_from_request
from helpers.auth import BasicObjectPermission
from products.lists.filters import BrandFilter, AvailFilter, ProductPropertyFilter, CategoryFilter, ProductFilter, \
    ProductGalleryFilter, NoContentProductFilter
from products.models import Brand, Avail, ProductProperty, Category, Product, ProductGallery
from products.serializers import BrandSerializer, AvailSerializer, ProductPropertySerializer, CategorySerializer, \
    ProductSerializer, ProductGallerySerializer, NoContentProductSimpleSerializer


class BrandListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)

    permission_codename = "get.brand"

    serializer_class = BrandSerializer
    filterset_class = BrandFilter
    ordering_fields = '__all__'
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return Brand.objects.all()


class AvailListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)

    permission_codename = "get.avail"

    serializer_class = AvailSerializer
    filterset_class = AvailFilter
    ordering_fields = '__all__'
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return Avail.objects.all()


class ProductPropertyListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)

    permission_codename = "get.product_property"

    serializer_class = ProductPropertySerializer
    filterset_class = ProductPropertyFilter
    ordering_fields = '__all__'
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return ProductProperty.objects.all()


class CategoryListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)

    permission_codename = "get.category"

    serializer_class = CategorySerializer
    filterset_class = CategoryFilter
    ordering_fields = '__all__'
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return Category.objects.all()


class ProductListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)

    permission_codename = "get.product"

    serializer_class = ProductSerializer
    filterset_class = ProductFilter
    ordering_fields = '__all__'
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return Product.objects.all()


class AffiliateForSaleProductsListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)

    permission_codename = "get.product"

    serializer_class = ProductSerializer
    filterset_class = ProductFilter
    ordering_fields = '__all__'
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        business = get_business_from_request(self.request)
        return Product.objects.filter(business=business.id)


class ProductGalleryListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)

    permission_codename = "get.product"

    serializer_class = ProductGallerySerializer
    filterset_class = ProductGalleryFilter
    ordering_fields = '__all__'
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return ProductGallery.objects.all()


class NoContentProductListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)

    permission_codename = "get.product"

    serializer_class = NoContentProductSimpleSerializer
    filterset_class = NoContentProductFilter
    ordering_fields = '__all__'
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return Product.objects.filter(
            Q(picture=None) |
            Q(explanation=None) |
            Q(summary_explanation=None) |
            Q(how_to_use=None) |
            Q(picture='') |
            Q(explanation='') |
            Q(summary_explanation='') |
            Q(how_to_use='')
        )