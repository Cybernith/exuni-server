from django.shortcuts import get_object_or_404
from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from financial_management.loggers.financial_logger import FinancialLogger
from financial_management.models import Payment, AuditAction, AuditSeverity
from financial_management.zarinpal import ZarinpalGateway
from helpers.functions import get_current_user
from server.gateway_configs import TRUSTED_GATEWAY_IP, GATEWAY_SECRET_PAYMENT_TOKEN
from server.settings import SERVER_URL, SECRET_KEY
from shop.models import ShopOrder
from financial_management.throttles import PaymentRateThrottle
import hmac
import hashlib

from subscription.models import DiscountCode


class StartZarinpalPaymentApiView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [PaymentRateThrottle]

    def post(self, request, order_id):

        order = get_object_or_404(ShopOrder, id=order_id, customer=get_current_user())

        if hasattr(order, 'bank_payment'):
            return Response({'detail': 'this order already have open payment'}, status=status.HTTP_400_BAD_REQUEST)

        payment = order.pay()
        callback_url = SERVER_URL + reverse('financial_management:zarinpal_callback')

        gateway = ZarinpalGateway(
            amount=order.final_amount,
            description=f'پرداخت سفارش {order.id}',
            callback_url=callback_url
        )

        try:
            result = gateway.request_payment()
            payment.reference_id = result['authority']
            payment.save()
            return Response({'payment_url': result['payment_url']})

        except Exception as exception:
            payment.delete()
            return Response({'detail': str(exception)}, status=status.HTTP_400_BAD_REQUEST)


class ZarinpalCallbackApiView(APIView):

    def get(self, request):
        authority = request.query_params.get('Authority')
        callback_status = request.query_params.get('Status')

        if callback_status != 'OK':
            return Response({'detail': 'payment failed'}, status=status.HTTP_400_BAD_REQUEST)

        payment = get_object_or_404(Payment, reference_id=authority)
        order = payment.shop_order

        gateway = ZarinpalGateway(
            amount=payment.amount,
            description=f'تایید پرداخت سفارش {order.id}',
            callback_url=''
        )

        result = gateway.verify_payment(authority)
        if result.get('data') and result['data'].get('code') == 100:
            payment.mark_as_success_payment(user=payment.user)
            FinancialLogger.log(
                user=payment.user,
                action=AuditAction.PAYMENT_ORDER,
                severity=AuditSeverity.INFO,
                payment=payment,
                ip_address=self.kwargs.get("ip"),
                user_agent=self.kwargs.get("agent"),
                extra_info={"amount": str(payment.amount)}
            )
            order.mark_as_paid(user=payment.user)
            return Response({'detail': 'payment verify was successfully', 'ref_id': result['data']['ref_id']},
                            status=status.HTTP_200_OK)
        else:
            payment.mark_as_failed_payment(user=payment.user)
            FinancialLogger.log(
                user=payment.user,
                action=AuditAction.PAYMENT_FAILED,
                severity=AuditSeverity.INFO,
                payment=payment,
                ip_address=self.kwargs.get("ip"),
                user_agent=self.kwargs.get("agent"),
                extra_info={"amount": str(payment.amount)}
            )

            return Response({'detail': 'payment verify failed'}, status=status.HTTP_400_BAD_REQUEST)


class StartPaymentApiView(APIView):
    throttle_classes = [PaymentRateThrottle]

    def post(self, request, order_id):
        order = get_object_or_404(ShopOrder, id=order_id, customer=request.user)

        if hasattr(order, 'bank_payment'):
            return Response({'detail': 'this order already have open payment'}, status=status.HTTP_400_BAD_REQUEST)

        gateway_name = 'gateway'

        payment = order.pay()
        gateway_url = f'https://gateway.com/pay?payment_id={payment.id}'

        return Response({
            'payment_id': payment.id,
            'gateway_url': gateway_url
        })


class PaymentCallbackApiView(APIView):
    permission_classes = [AllowAny]

    @staticmethod
    def verify_signature(payload, signature, secret):
        expected = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, signature)

    def post(self, request):

        payload = request.body.decode()
        signature = request.headers.get('X-Gateway-Signature')
        client_ip = request.META.get('REMOTE_ADDR')
        gateway_token = request.headers.get('X-Gateway-Token')

        if gateway_token != GATEWAY_SECRET_PAYMENT_TOKEN:
            return Response({'detail': 'invalid gateway token'}, status=status.HTTP_403_FORBIDDEN)

        if client_ip not in TRUSTED_GATEWAY_IP:
            return Response({'detail': 'Unauthorized IP'}, status=status.HTTP_403_FORBIDDEN)

        if not self.verify_signature(payload, signature, SECRET_KEY):
            return Response({'detail': 'invalid gateway signature'}, status=status.HTTP_403_FORBIDDEN)

        payment_id = request.data.get('payment_id')
        success = request.data.get('success')
        payment = get_object_or_404(Payment, id=payment_id)

        if success:
            payment.mark_as_success_payment(user=payment.user)
            payment.shop_order.mark_as_paid(user=payment.user)

            return Response({'detail': 'payment verify was successfully'}, status=status.HTTP_201_CREATED)

        else:
            payment.mark_as_failed_payment(user=payment.user)
            return Response({'detail': 'transaction verify failed'}, status=status.HTTP_400_BAD_REQUEST)


class VerifyDiscountCodeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        discount_code = request.data.get('discount_code')
        order_amount = request.data.get('order_amount')
        try:
            discount_code: DiscountCode = DiscountCode.objects.get(code=discount_code)
        except DiscountCode.DoesNotExist:
            raise ValidationError("کد تخفیف معتبر نمی باشد")
        discount_code.verify()

        return Response({
            'discount_code_id': discount_code.id,
            'discount_amount': discount_code.get_discount_amount(order_amount)
        })
