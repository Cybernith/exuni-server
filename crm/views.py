import datetime

from django.shortcuts import render, get_object_or_404
from django.utils.dateparse import parse_date
from  rest_framework import generics, permissions
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAdminUser

from crm.models import ShopProductViewLog
from crm.serializer import ShopProductViewLogCreateSerializer
from helpers.functions import date_to_str
from products.models import Product

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Q
from django.db.models.functions import TruncMonth

from products.serializers import ProductForLogSerializer


class ShopProductViewLogApiView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ShopProductViewLogCreateSerializer

    def get_queryset(self):
        product = get_object_or_404(Product, pk=self.kwargs['product_id'])
        return ShopProductViewLog.objects.filter(product=product)


class ProductViewSummaryAPIView(APIView):
    def get(self, request, product_id):
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        total_views = ShopProductViewLog.objects.filter(product=product).count()

        monthly_qs = (
            ShopProductViewLog.objects
            .filter(product=product)
            .annotate(month=TruncMonth('created_at'))
            .values('month')
            .annotate(views=Count('id'))
            .order_by('month')
        )
        monthly_data = [
            {
                "month": entry['month'].strftime("%Y-%m"),
                "views": entry['views']
            }
            for entry in monthly_qs
        ]

        return Response({
            "product_id": product_id,
            "total_views": total_views,
            "monthly_views": monthly_data
        }, status=status.HTTP_200_OK)


class ProductVisitReportView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, product_id):
        today = datetime.datetime.now().date()
        month_start = today.replace(day=1)
        year_start = today.replace(month=1, day=1)

        logs = ShopProductViewLog.objects.filter(product_id=product_id)

        total = logs.count()
        authenticated = logs.filter(user__isnull=False).count()
        anonymous = logs.filter(user__isnull=True).count()
        current_month_view_count = logs.filter(created_at_date_gte=month_start).count()
        current_year_view_count = logs.filter(created_at_date_gte=year_start).count()

        browser_statistics = logs.values('browser_type').annotate(count=Count('id')).order_by('-count')
        device_statistics = logs.values('device_type').annotate(count=Count('id')).order_by('-count')
        daily_statistics = logs.extra({'day': "date(created_at)"}).values('day').annotate(
            count=Count('id')).order_by('day')

        return Response({
            'total_visits': total,
            'authenticated_visits': authenticated,
            'anonymous_visits': anonymous,
            'current_month_visits': current_month_view_count,
            'current_year_visits': current_year_view_count,
            'browsers': list(browser_statistics),
            'devices': list(device_statistics),
            'daily_visits': list(daily_statistics),
        }, status=status.HTTP_200_OK)


class ProductInRangeVisitReportView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, product_id):
        start = request.query_params.get('start_date')
        end = request.query_params.get('end_date')

        try:
            if start:
                start_date = parse_date(start)
            else:
                start_date = None
            if start:
                end_date = parse_date(end)
            else:
                end_date = None
        except:
            return Response({'detail': 'invalid date format'}, status=status.HTTP_400_BAD_REQUEST)

        if start and end:
            logs = ShopProductViewLog.objects.filter(
                Q(product_id=product_id) &
                Q(created_at__date__gte=start_date) &
                Q(created_at__date__lte=end_date)
            )
        elif start and not end:
            logs = ShopProductViewLog.objects.filter(
                Q(product_id=product_id) &
                Q(created_at__date__gte=start_date)
            )

        elif end and not start:
            logs = ShopProductViewLog.objects.filter(
                Q(product_id=product_id) &
                Q(created_at__date__lte=end_date)
            )
        else:
            logs = ShopProductViewLog.objects.filter(product_id=product_id)

        total = logs.count()
        authenticated = logs.filter(user__isnull=False).count()
        anonymous = logs.filter(user__isnull=True).count()
        browser_statistics = logs.values('browser_type').annotate(count=Count('id')).order_by('-count')
        device_statistics = logs.values('device_type').annotate(count=Count('id')).order_by('-count')
        daily_statistics = logs.extra({'day': "date(created_at)"}).values('day').annotate(
            count=Count('id')).order_by('day')

        return Response({
            'start': date_to_str(start_date) if start_date else 'از ابتدا ',
            'end': date_to_str(end_date) if end else 'تا امروز ',
            'total_visits': total,
            'authenticated_visits': authenticated,
            'anonymous_visits': anonymous,
            'browsers': list(browser_statistics),
            'devices': list(device_statistics),
            'daily_visits': list(daily_statistics),
        }, status=status.HTTP_200_OK)


class UserTopVisitedProductsAPIView(ListAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = ProductForLogSerializer

    def get_queryset(self):
        try:
            limit = int(self.request.query_params.get('limit', 10))
            if limit < 1:
                raise ValueError
        except ValueError:
            raise ValidationError({"limit": "Must be a positive integer."})

        user_id = self.kwargs['user_id']
        queryset = Product.objects.annotate(
            user_visits=Count(
                'views_log',
                filter=Q(views_log__user_id=user_id)
            )
        ).filter(
            user_visits__gt=0
        ).order_by(
            '-user_visits'
        )[:limit]

        return queryset
