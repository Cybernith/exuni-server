import jdatetime
from django.db.models import Q, Sum, F, ExpressionWrapper
from django.http import Http404
from rest_framework import generics, status
from django.db.models.fields import DecimalField
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from rest_framework.response import Response
from helpers.auth import BasicObjectPermission
from products.models import Product
from products.shop.filters import ShopProductSimpleFilter

from shop.exuni_admin.filters import AdminShopOrderFilter
from shop.exuni_admin.srializers import AdminShopOrderSimpleSerializer, AdminShopOrderDetailSerializer, \
    AdminProductsListSerializers
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
        return ShopOrder.objects.filter(status=ShopOrder.PAID).select_related(
            'shipment_address', 'customer', 'packager', 'print_by').prefetch_related('items__product')


class BulkChangeStatusToProcessingView(APIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission, IsAdminUser)
    permission_codename = "update.shop_order"

    def post(self, request):
        to_id = request.data.get('to_id')
        from_id = request.data.get('from_id')
        is_printed = request.data.get('is_printed', 'all')
        order_id = request.data.get('id')
        date = request.data.get('date')

        filters = Q(status=ShopOrder.PAID)

        if to_id and from_id:
            filters &= Q(id__lte=to_id) & Q(id__gte=from_id)

        if order_id:
            filters &= Q(id=order_id)

        if is_printed != 'all':
            filters &= Q(is_printed=is_printed != 'false')

        if date:
            try:
                parts = date.split('-')
                if len(parts) == 3:
                    j_date = jdatetime.date(
                        year=int(parts[0]),
                        month=int(parts[1]),
                        day=int(parts[2])
                    )
                    g_date = j_date.togregorian()
                    filters &= Q(date_time__date=g_date)
            except Exception:
                pass

        orders = ShopOrder.objects.filter(filters)
        updated_count = orders.update(status=ShopOrder.PROCESSING)

        return Response({
            'message': f'{updated_count} سفارش به وضعیت در حال بسته بندی تغییر کرد.'
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
        to_id = request.data.get('to_id')
        from_id = request.data.get('from_id')
        is_printed = request.data.get('is_printed', 'all')
        order_id = request.data.get('id')
        packager = request.data.get('packager')
        date = request.data.get('date')

        filters = Q(status__in=[ShopOrder.PAID, ShopOrder.PROCESSING])

        if to_id and from_id:
            filters &= Q(id__lte=to_id) & Q(id__gte=from_id)

        if order_id:
            filters &= Q(id=order_id)

        if packager:
            filters &= Q(packager__id=packager)

        if is_printed != 'all':
            filters &= Q(is_printed=is_printed != 'false')

        if date:
            try:
                parts = date.split('-')
                if len(parts) == 3:
                    j_date = jdatetime.date(
                        year=int(parts[0]),
                        month=int(parts[1]),
                        day=int(parts[2])
                    )
                    g_date = j_date.togregorian()
                    filters &= Q(date_time__date=g_date)
            except Exception:
                pass

        orders = ShopOrder.objects.filter(filters)
        updated_count = orders.update(status=ShopOrder.SHIPPED)

        return Response({
            'message': f'{updated_count} سفارش به وضعیت ارسال شد تغییر کرد.'
        }, status=200)


class AdminOrderDetailApiView(APIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)
    permission_basename = 'shop_order'

    def get_object(self, pk):
        try:
            return ShopOrder.objects.select_related('shipment_address', 'customer').prefetch_related('history', 'items').get(pk=pk)
        except ShopOrder.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        query = self.get_object(pk)
        serializers = AdminShopOrderDetailSerializer(query)
        return Response(serializers.data, status=status.HTTP_200_OK)


class OrdersSumAPIView(APIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)
    permission_basename = 'shop_order'


    def get(self, request):
        total_expression = ExpressionWrapper(
            F('total_price') + F('post_price'),
            output_field=DecimalField(max_digits=18, decimal_places=2)
        )

        shipped_total = ShopOrder.objects.filter(status=ShopOrder.SHIPPED).aggregate(
            total_sum=Sum(total_expression)
        )['total_sum'] or 0

        paid_total = ShopOrder.objects.filter(status=ShopOrder.PAID).aggregate(
            total_sum=Sum(total_expression)
        )['total_sum'] or 0

        return Response({"shipped_total": shipped_total, "paid_total": paid_total}, status=status.HTTP_200_OK)


class AdminShopProductSimpleListView(generics.ListAPIView):
    serializer_class = AdminProductsListSerializers
    filterset_class = ShopProductSimpleFilter
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return Product.objects.exclude(product_type=Product.VARIATION).select_related('brand')
