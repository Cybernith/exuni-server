from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum, F, Q
from rest_framework.pagination import LimitOffsetPagination
from datetime import datetime, timedelta

from financial_management.software_development_profit.serializers import SoftwareDevelopmentShopOrderSimpleSerializer
from helpers.models import DECIMAL
from shop.api_serializers import ApiCustomerShopOrderItemSerializer
from shop.models import ShopOrderItem, ShopOrder


class SoftwareDevelopmentProfitReport(APIView):

    def get(self, request):
        from_date = request.query_params.get('from_date')
        to_date = request.query_params.get('to_date')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        order_qs = ShopOrder.objects.filter(
            status__in=[
                ShopOrder.PAID, ShopOrder.PROCESSING,
                ShopOrder.PACKED, ShopOrder.SHIPPED
            ]
        )

        filtered_qs = order_qs

        if start_date:
            filtered_qs = filtered_qs.filter(date_time__date__gt=start_date)

        if end_date:
            end_date = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
            filtered_qs = filtered_qs.filter(date_time__date__lte=end_date)

        if from_date:
            filtered_qs = filtered_qs.filter(date_time__date__gte=from_date)
        if to_date:
            filtered_qs = filtered_qs.filter(date_time__date__lte=to_date)

        orders = filtered_qs.prefetch_related('items')
        order_qs = order_qs.prefetch_related('items').select_related('product', 'product__currency')

        paginator = LimitOffsetPagination()
        paginated_orders = paginator.paginate_queryset(orders, request)

        currency_ids = [14, 15, 17]
        result = []
        for order in paginated_orders:
            filtered_items = ShopOrderItem.objects.filter(shop_order=order).filter(
                Q(product__currency_id__in=currency_ids) | Q(product__currency__isnull=True)
            )
            order_data = {
                "order": SoftwareDevelopmentShopOrderSimpleSerializer(order).data,
                "items": ApiCustomerShopOrderItemSerializer(filtered_items, many=True).data
            }
            result.append(order_data)

        current_items = ShopOrderItem.objects.filter(shop_order__in=paginated_orders).filter(
                Q(product__currency_id__in=currency_ids) | Q(product__currency__isnull=True)
            )
        page_total_price = current_items.aggregate(
            total=Sum(F('price') * F('product_quantity'), output_field=DECIMAL())
        )['total'] or 0

        total_items = ShopOrderItem.objects.filter(shop_order__in=order_qs).filter(
                Q(product__currency_id__in=currency_ids) | Q(product__currency__isnull=True)
            )
        total_price = total_items.aggregate(
            total=Sum(F('price') * F('product_quantity'), output_field=DECIMAL())
        )['total'] or 0


        return Response({
            "count": order_qs.count(),
            "orders": result,
            "summary": {
                "total_order_count": order_qs.count(),
                "total_price": total_price,
            },
            "pagination_summary": {
                "total_order_count": len(paginated_orders),
                "total_price": page_total_price,
            }
        })
