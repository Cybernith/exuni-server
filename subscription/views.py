import json
from urllib.request import Request
from django.db.models import QuerySet, F, Window, Sum, DecimalField, Q
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404, redirect
from rest_framework import generics
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.parsers import FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError

from helpers.auth import BasicCRUDPermission
from server.configs import PEC
from server.settings import DEVELOPING
from subscription.filters import TransactionFilter
from subscription.models import Transaction, Factor, FactorItem, DiscountCode
from subscription.serializers import FactorListSerializer, TransactionListSerializer, UserTurnoverSerializer,\
    FactorRetrieveSerializer
import zeep
from django_filters import rest_framework as filters
from helpers.filters import BASE_FIELD_FILTERS


class TransactionCallbackView(APIView):
    parser_classes = (FormParser,)

    @staticmethod
    def get_redirect_URL(success):
        if success:
            if DEVELOPING:
                return 'http://localhost:8080/panel/wallet'
            else:
                return 'https://app.sobhan.net/panel/wallet'
        else:
            if DEVELOPING:
                return 'http://localhost:8080/panel/transactionFailed'
            else:
                return 'https://app.sobhan.net/panel/transactionFailed'

    @staticmethod
    def get_redirect_URL_after_extend_or_add_user(success):
        if success:
            if DEVELOPING:
                return 'http://localhost:8080/panel/home'
            else:
                return 'https://app.sobhan.net/panel/home'
        else:
            if DEVELOPING:
                return 'http://localhost:8080/panel/transactionFailed'
            else:
                return 'https://app.sobhan.net/panel/transactionFailed'

    def post(self, request):
        return self.callback(request)

    def callback(self, request: Request):
        data = request.data

        transaction = Transaction.objects.get(_order_id=data['OrderId'])
        transaction._gateway_callback = data
        transaction.save()

        # check if payment was successful
        status = data['status']
        if status == '0' and int(data.get('RRN')) > 0:
            client = zeep.Client(
                "https://pec.shaparak.ir/NewIPGServices/Confirm/ConfirmService.asmx?WSDL"
            )
            confirm_res = client.service.ConfirmPayment({
                'LoginAccount': PEC['PIN_CODE'],
                'Token': data['Token']
            })
            confirm_status = str(confirm_res['Status'])
            if confirm_status == '0':
                transaction.success()

                if transaction.factor:
                    return redirect(self.get_redirect_URL(True))
                else:
                    return redirect('https://app.sobhan.net/panel/wallet?success=true')
        else:
            return redirect(self.get_redirect_URL(False))

        return Response({
            'order_id': data['OrderId'],
            'token': data['Token'],
            'status': data['status'],
            'RRN': data['RRN'],
            'confirm_res': confirm_res['Status']
        })


class TransactionListCreateView(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = TransactionListSerializer
    pagination_class = LimitOffsetPagination
    ordering_fields = '__all__'
    filterset_class = TransactionFilter

    def get_queryset(self):
        return Transaction.objects.prefetch_related('wallet').filter(user=self.request.user).all()

    def post(self, request: Request, *args, **kwargs) -> Response:
        user = request.user
        data = request.data
        amount = data['amount']

        transaction = Transaction.create_transaction(Transaction.DEPOSIT, user, amount, None)

        return Response({
            'redirect_url': Transaction.get_redirect_url(transaction)
        })

def user_name_filter(queryset, name, value):
    return queryset.filter(Q(user__first_name__contains=value) | Q(user__last_name__contains=value))

class SubscriptionFactorFilter(filters.FilterSet):
    after_discount_amount = filters.NumberFilter(field_name='after_discount_amount')
    after_discount_amount__icontains = filters.NumberFilter(field_name='after_discount_amount', lookup_expr='icontains')
    after_discount_amount__gte = filters.NumberFilter(field_name='after_discount_amount', lookup_expr='gte')
    after_discount_amount__lte = filters.NumberFilter(field_name='after_discount_amount', lookup_expr='lte')
    added_value_tax = filters.NumberFilter(field_name='added_value_tax')
    added_value_tax__icontains = filters.NumberFilter(field_name='added_value_tax', lookup_expr='icontains')
    added_value_tax__gte = filters.NumberFilter(field_name='added_value_tax', lookup_expr='gte')
    added_value_tax__lte = filters.NumberFilter(field_name='added_value_tax', lookup_expr='lte')
    payable_amount = filters.NumberFilter(field_name='payable_amount')
    payable_amount__icontains = filters.NumberFilter(field_name='payable_amount', lookup_expr='icontains')
    payable_amount__gte = filters.NumberFilter(field_name='payable_amount', lookup_expr='gte')
    payable_amount__lte = filters.NumberFilter(field_name='payable_amount', lookup_expr='lte')

    created_at = filters.DateFilter(field_name='created_at__date')
    created_at__gte = filters.DateFilter(field_name='created_at__date', lookup_expr='gte')
    created_at__lte = filters.DateFilter(field_name='created_at__date', lookup_expr='lte')
    created_at__icontains = filters.CharFilter(field_name='created_at__date', lookup_expr='icontains')
    time = filters.TimeFilter(field_name='time')
    time__gte = filters.TimeFilter(field_name='time', lookup_expr='gte')
    time__lte = filters.TimeFilter(field_name='time', lookup_expr='lte')
    time__icontains = filters.CharFilter(field_name='time', lookup_expr='icontains')
    user_name = filters.CharFilter(method=user_name_filter)

    class Meta:
        model = Factor
        fields = {
            'id': ('exact',),
            'is_paid': ('exact',),
            'amount': BASE_FIELD_FILTERS,
            'discount_amount': BASE_FIELD_FILTERS,
            'created_by': ('exact',),
        }


class FactorListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = FactorListSerializer
    pagination_class = LimitOffsetPagination
    ordering_fields = '__all__'
    filterset_class = SubscriptionFactorFilter

    def get_queryset(self) -> QuerySet:
        return Factor.objects.filter(user=self.request.user)


class FactorRetrieveView(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = FactorRetrieveSerializer

    def get_queryset(self) -> QuerySet:
        return Factor.objects.filter(user=self.request.user).prefetch_related('items')


class VerifyDiscountCodeView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        discount_code = request.data.get('discount_code')
        factor_amount = request.data.get('factor_amount')
        try:
            discount_code: DiscountCode = DiscountCode.objects.get(code=discount_code)
        except DiscountCode.DoesNotExist:
            raise ValidationError("کد تخفیف معتبر نمی باشد")
        discount_code.verify()

        return Response({
            'discount_amount': discount_code.get_discount_amount(factor_amount)
        })


class UserTurnover(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserTurnoverSerializer
    pagination_class = LimitOffsetPagination
    ordering_fields = '__all__'
    filterset_class = TransactionFilter

    def get_queryset(self) -> QuerySet:
        return Transaction.objects.filter(user=self.request.user, _is_successful=True).annotate(
            cumulative_bed=Coalesce(
                Window(expression=Sum('bed'), order_by=[F('datetime'), ]),
                0,
                output_field=DecimalField()
            ),
            cumulative_bes=Coalesce(
                Window(expression=Sum('bes'), order_by=[F('datetime'), ]),
                0,
                output_field=DecimalField()
            ),
            cumulative_remain=Coalesce(
                Window(expression=Sum('bed'), order_by=[F('datetime'), ]),
                0,
                output_field=DecimalField()
            ) - Coalesce(
                Window(expression=Sum('bes'), order_by=[F('datetime'), ]),
                0,
                output_field=DecimalField()
            ),
        ).order_by('datetime')

