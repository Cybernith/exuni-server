from rest_framework import generics
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from helpers.auth import BasicObjectPermission

from shop.exuni_admin.filters import AdminShopOrderFilter
from shop.exuni_admin.srializers import AdminShopOrderSimpleSerializer
from shop.models import ShopOrder


class AdminShopOrderListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission, IsAdminUser)
    permission_codename = "get.shop_order"

    serializer_class = AdminShopOrderSimpleSerializer
    filterset_class = AdminShopOrderFilter
    ordering_fields = '__all__'
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return ShopOrder.objects.exclude(status=ShopOrder.PENDING)


