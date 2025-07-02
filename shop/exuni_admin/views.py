from rest_framework import generics
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from helpers.auth import BasicObjectPermission

from shop.api_serializers import ApiCustomerShopOrderSimpleSerializer
from shop.filters import ShopOrderFilter
from shop.models import ShopOrder


class AdminShopOrderListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission, IsAdminUser)
    permission_codename = "get.shop_order"

    serializer_class = ApiCustomerShopOrderSimpleSerializer
    filterset_class = ShopOrderFilter
    ordering_fields = '__all__'
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return ShopOrder.objects.all()


