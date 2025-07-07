from rest_framework import generics
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from rest_framework.response import Response
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
        return ShopOrder.objects.exclude(status=ShopOrder.PENDING).select_related('shipment_address', 'customer')


class AdminPaidShopOrderListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission, IsAdminUser)
    permission_codename = "get.shop_order"

    serializer_class = AdminShopOrderSimpleSerializer
    filterset_class = AdminShopOrderFilter
    ordering_fields = '__all__'
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return ShopOrder.objects.filter(status=ShopOrder.PAID).select_related('shipment_address', 'customer')


class BulkChangeStatusToProcessingView(APIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission, IsAdminUser)
    permission_codename = "update.shop_order"

    def post(self, request):
        order_ids = request.data.get('order_ids', [])
        if not isinstance(order_ids, list):
            return Response({'error': 'سفارش ها باید لیستی از شناسه‌ها باشد.'}, status=400)

        orders = ShopOrder.objects.filter(id__in=order_ids, status=ShopOrder.PAID)
        updated_count = 0

        for order in orders:
            order.status = ShopOrder.PROCESSING
            order.save()
            updated_count += 1
        return Response({
            'message': f'{updated_count} سفارش به وضعیت درحال بسته‌بندی تغییر کرد.',
            'updated_ids': [order.id for order in orders]
        }, status=200)


class AdminProcessingShopOrderListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission, IsAdminUser)
    permission_codename = "get.shop_order"

    serializer_class = AdminShopOrderSimpleSerializer
    filterset_class = AdminShopOrderFilter
    ordering_fields = '__all__'
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return ShopOrder.objects.filter(status=ShopOrder.PROCESSING).select_related('shipment_address', 'customer')


class BulkChangeStatusToPackedView(APIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission, IsAdminUser)
    permission_codename = "update.shop_order"

    def post(self, request):
        order_ids = request.data.get('order_ids', [])
        if not isinstance(order_ids, list):
            return Response({'error': 'سفارش ها باید لیستی از شناسه‌ها باشد.'}, status=400)

        orders = ShopOrder.objects.filter(id__in=order_ids, status=ShopOrder.PROCESSING)
        updated_count = 0

        for order in orders:
            order.status = ShopOrder.PACKED
            order.save()
            updated_count += 1
        return Response({
            'message': f'{updated_count} سفارش به وضعیت بسته‌بندی شد تغییر کرد.',
            'updated_ids': [order.id for order in orders]
        }, status=200)


class BulkChangeStatusToShippedView(APIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission, IsAdminUser)
    permission_codename = "update.shop_order"

    def post(self, request):
        ShopOrder.objects.filter(status=ShopOrder.PAID).update(status=ShopOrder.SHIPPED)

        return Response({
            'message': 'به وضعیت ارسال شد تغییر کرد.',
        }, status=200)
