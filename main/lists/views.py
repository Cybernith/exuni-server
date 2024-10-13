from rest_framework import generics
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from helpers.auth import BasicObjectPermission
from main.lists.filters import BusinessFilter, StoreFilter, CurrencyFilter, SupplierFilter
from main.models import Business, Store, Currency, Supplier
from main.serializers import BusinessSerializer, StoreSerializer, CurrencySerializer, SupplierSerializer


class BusinessListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)

    permission_codename = "get.business"

    serializer_class = BusinessSerializer
    filterset_class = BusinessFilter
    ordering_fields = '__all__'
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return Business.objects.all()


class StoreListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)

    permission_codename = "get.store"

    serializer_class = StoreSerializer
    filterset_class = StoreFilter
    ordering_fields = '__all__'
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return Store.objects.all()


class CurrencyListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)

    permission_codename = "get.currency"

    serializer_class = CurrencySerializer
    filterset_class = CurrencyFilter
    ordering_fields = '__all__'
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return Currency.objects.all()


class SupplierListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)

    permission_codename = "get.supplier"

    serializer_class = SupplierSerializer
    filterset_class = SupplierFilter
    ordering_fields = '__all__'
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return Supplier.objects.all()
