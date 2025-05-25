import datetime

from django.core.cache import cache
from django.shortcuts import render, get_object_or_404
from django.utils.dateparse import parse_date
from  rest_framework import generics, permissions
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from crm.functions import save_search_log, get_recommended_products
from crm.models import ShopProductViewLog, SearchLog, Notification, UserNotification
from crm.serializer import ShopProductViewLogCreateSerializer, NotificationCreateSerializer, \
    UserNotificationRetrieveSerializer
from crm.throttles import UserFinalSearchLogRateThrottle, AnonFinalSearchLogRateThrottle
from helpers.functions import date_to_str, get_current_user
from products.models import Product

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Q, OuterRef, Exists
from django.db.models.functions import TruncMonth

from products.serializers import ProductForLogSerializer
from products.shop.serializers import ShopProductsListSerializers
from shop.api_serializers import ApiProductsListSerializers
from shop.models import ShopOrderItem, ShopOrder
from users.models import User
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie


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
    serializer_class = ApiProductsListSerializers

    def get_queryset(self):
        try:
            limit = int(self.request.query_params.get('limit', 10))
            if limit < 1:
                raise ValueError
        except ValueError:
            raise ValidationError({"limit": "Must be a positive integer."})

        queryset = Product.objects.annotate(
            user_visits=Count(
                'views_log',
                filter=Q(views_log__user=get_current_user())
            )
        ).filter(
            user_visits__gt=0
        ).order_by(
            '-user_visits'
        )[:limit]

        return queryset


class RegisterFinalSearchLogAPIView(APIView):
    throttle_classes = [UserFinalSearchLogRateThrottle, AnonFinalSearchLogRateThrottle]

    def post(self, request):
        search_value = request.data.get('search_value', '').strip()
        search_type = request.data.get('search_type', SearchLog.RAW_TEXT).strip()
        if not search_value:
            return Response(status=status.HTTP_204_NO_CONTENT)
        save_search_log(request, query_value=search_value, search_type=search_type)

        return Response(status=status.HTTP_204_NO_CONTENT)


class RecommendedProductsAPIView(APIView):
    serializer_class = ApiProductsListSerializers
    pagination_class = None
    permission_classes = [IsAuthenticated]
    CACHE_TIMEOUT = 60

    @method_decorator(cache_page(CACHE_TIMEOUT))
    @method_decorator(vary_on_cookie)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        return Product.objects.filter(
            id__in=get_recommended_products(
                user=get_current_user(),
                limit=10
            )
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class CreateNotificationAPIView(APIView):
    def post(self, request):
        serializer = NotificationCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer_data = serializer.data
            users = User.objects.all()
            filter_parameter = serializer_data['exclude']
            if serializer_data['seen_product']:
                users = users.annotate(
                    is_seened=Exists(
                        ShopProductViewLog.objects.filter(
                            Q(user=OuterRef('pk')) & Q(product=serializer_data['seen_product']))
                    )).filter(is_seened=filter_parameter)
            if serializer_data['seen_category']:
                users = users.annotate(
                    is_seened=Exists(
                        ShopProductViewLog.objects.filter(
                            Q(user=OuterRef('pk')) & Q(category=serializer_data['seen_category']))
                    )).filter(is_seened=filter_parameter)
            if serializer_data['searched_about']:
                users = users.annotate(
                    is_searched=Exists(
                        SearchLog.objects.filter(
                            Q(user=OuterRef('pk')) & Q(query_value=serializer_data['searched_about']))
                    )).filter(is_searched=filter_parameter)
            if serializer_data['purchased_product']:
                users = users.annotate(
                    is_purchased=Exists(
                        ShopOrderItem.objects.filter(
                            Q(shop_order__customer=OuterRef('pk')) &
                            Q(shop_order__status=ShopOrder.DELIVERED) &
                            Q(product=serializer_data['purchased_product']))
                    )).filter(is_purchased=filter_parameter)
            if serializer_data['more_than_amount']:
                users = users.annotate(
                    is_more_than_amount=Exists(
                        ShopOrder.objects.filter(
                            Q(customer=OuterRef('pk')) &
                            Q(status=ShopOrder.DELIVERED) &
                            Q(total_price__gte=serializer_data['more_than_amount']))
                    )).filter(is_more_than_amount=filter_parameter)
            send_datetime = serializer_data['send_datetime'] if serializer_data['send_datetime'] else None
            if serializer_data['send_sms']:
                notification = Notification.objects.create(
                    type=Notification.SEND_BY_ADMIN,
                    send_sms=True,
                    sms_text=serializer_data['sms_text'],
                    send_datetime=send_datetime,
                    receivers=users
                )
            else:
                notification = Notification.objects.create(
                    send_datetime=send_datetime,
                    type=Notification.SEND_BY_ADMIN,
                    send_sms=False,
                    notification_title=serializer_data['notification_title'],
                    notification_explanation=serializer_data['notification_explanation'],
                    notification_link=serializer_data['notification_link'],
                    product__id=serializer_data['product'],
                    receivers=users
                )
            notification.create_user_notifications()

            return Response({'detail': f"{len(notification)} notifications created."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserCurrentNotificationsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_objects(self):
        return UserNotification.objects.filter(
            Q(user=get_current_user()) &
            Q(notification__send_datetime__lte=datetime.datetime.now())
        )

    def get(self, request):
        query = self.get_objects()
        query.update(notification_status=UserNotification.NOT_READ)

        serializers = UserNotificationRetrieveSerializer(query, many=True)
        return Response(serializers.data, status=status.HTTP_200_OK)


class UserCurrentNotificationsBySortAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_objects(self):
        return UserNotification.objects.filter(
            Q(user=get_current_user()) &
            (Q(notification__send_datetime__lte=datetime.datetime.now()) | Q(notification__send_datetime__isnull=True))
        ).select_related('notification').order_by('-notification__send_datetime')

    def get_activities_objects(self):
        return self.get_objects().filter(notification__sort=Notification.ACTIVITIES)


    def get_offer_objects(self):
        return self.get_objects().filter(notification__sort=Notification.OFFERS)


    def get_order_objects(self):
        return self.get_objects().filter(notification__sort=Notification.ORDERS)

    def get(self, request):
        user = get_current_user()
        activities_objects = self.get_activities_objects()
        activities_objects.update(notification_status=UserNotification.NOT_READ)
        offer_objects = self.get_offer_objects()
        offer_objects.update(notification_status=UserNotification.NOT_READ)
        order_objects = self.get_order_objects()
        order_objects.update(notification_status=UserNotification.NOT_READ)

        return Response(
            {
                'activities': UserNotificationRetrieveSerializer(activities_objects, many=True).data,
                'offer': UserNotificationRetrieveSerializer(offer_objects, many=True).data,
                'order': UserNotificationRetrieveSerializer(order_objects, many=True).data,
            }, status=status.HTTP_200_OK)


class MarkNotificationAsReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, notification_id):
        user_notification = get_object_or_404(UserNotification, id=notification_id, user=get_current_user())
        user_notification.mark_as_read()
        return Response({'detail': 'Notification marked as read.'}, status=status.HTTP_200_OK)
