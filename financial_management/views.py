from decimal import Decimal
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from financial_management.loggers.financial_logger import FinancialLogger
from financial_management.models import Payment, AuditAction, AuditSeverity, Discount, DiscountAction
from financial_management.serivces.discount_evaluator import evaluate_discount
from financial_management.serivces.wallet_top_up_service import WalletTopUpRequestService, WalletTopUpService
from financial_management.zarinpal import ZarinpalGateway
from helpers.functions import get_current_user
from products.models import Product
from server.gateway_configs import TRUSTED_GATEWAY_IP, GATEWAY_SECRET_PAYMENT_TOKEN
from server.settings import SERVER_URL, SECRET_KEY, FRONT_URL
from shop.models import ShopOrder
from financial_management.throttles import PaymentRateThrottle
import hmac
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from subscription.models import DiscountCode
import hashlib
import json
from django.core.cache import cache


class StartZarinpalPaymentApiView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [PaymentRateThrottle]

    def post(self, request, order_id):

        order = get_object_or_404(ShopOrder, id=order_id, customer=get_current_user())

        if hasattr(order, 'bank_payment'):
            return Response({'detail': 'this order already have open payment'}, status=status.HTTP_400_BAD_REQUEST)

        if request.data.get('use_wallet', False):
            payment = order.pay_with_wallet
            if not payment:
                return Response({'payment_url': '/payment/result?status=success'})
        else:
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
            if order.discount_code:
                order.discount_code.use()
            order.mark_as_paid()
            return redirect(f'{FRONT_URL}/payment/success?orderId={order.id}')
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

            return redirect(f'{FRONT_URL}/payment/fail?orderId={order.id}')


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
            payment.shop_order.mark_as_paid()

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
            'discount_code': discount_code,
            'discount_amount': discount_code.get_discount_amount(order_amount)
        })


def filter_discount_results(results):
    discounts = []
    free_shipping = []

    for res in results:
        if res['type'] == DiscountAction.FREE_SHIPPING:
            free_shipping.append(res)
        else:
            discounts.append(res)

    return discounts, free_shipping


class DiscountCheckAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @staticmethod
    def generate_cart_hash(cart_items):
        sorted_items = sorted(cart_items, key=lambda x: x['product'])
        cart_str = json.dumps(sorted_items, sort_keys=True)
        return hashlib.md5(cart_str.encode('utf-8')).hexdigest()

    def get_discounts_from_cache_or_db(self, user_id, enriched_cart_items, total_price):
        cart_hash = self.generate_cart_hash([
            {"product": item["product"].id, "quantity": item["quantity"]}
            for item in enriched_cart_items
        ])
        cache_key = f"discounts_{user_id}_{cart_hash}"

        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        active_discounts = Discount.objects.filter(is_active=True).prefetch_related(
            "conditions__category_condition__categories",
            "conditions__product_condition__products",
            "conditions__brand_condition__brands",
            "conditions__user_condition__users"
        )
        results = []
        for discount in active_discounts:
            result = evaluate_discount(discount, enriched_cart_items, user_id, total_price)
            if result:
                results.append(result)

        cache.set(cache_key, results, timeout=300)
        return results

    @staticmethod
    def calculate_cart_total(cart_items, product_map):
        total = Decimal("0.00")
        for item in cart_items:
            product = product_map[item['product']]
            total += Decimal(product.price) * item['quantity']
        return total

    def post(self, request):
        user = request.user
        cart_items_data = request.data.get("cart_items", [])

        product_ids = [item["product"] for item in cart_items_data]
        products = Product.objects.filter(id__in=product_ids)
        product_map = {p.id: p for p in products}

        enriched_cart_items = [
            {"product": product_map[item["product"]], "quantity": item["quantity"]}
            for item in cart_items_data if item["product"] in product_map
        ]

        total_price = self.calculate_cart_total(cart_items_data, product_map)

        raw_discounts = self.get_discounts_from_cache_or_db(user.id, enriched_cart_items, total_price)

        discounts, free_shipping = filter_discount_results(raw_discounts)

        return Response({
            "discounts": DiscountResultSerializer(discounts, many=True).data,
            "free_shipping": DiscountResultSerializer(free_shipping, many=True).data
        })


class StartZarinpalWalletTopUPApiView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [PaymentRateThrottle]

    def post(self, request):
        user = get_current_user()
        top_up_amount = request.data.get('top_up_amount', None)

        try:
            top_up_amount = int(top_up_amount)
        except (TypeError, ValueError):
            return Response({'detail': 'Invalid amount'}, status=status.HTTP_400_BAD_REQUEST)

        if not top_up_amount or top_up_amount < 100000:
            return Response({'detail': 'amount should be positive and greater than 100,000 rial'},
                            status=status.HTTP_400_BAD_REQUEST)

        payment = Payment.objects.create(
            user=user,
            amount=top_up_amount,
            gateway='zarinpal',
            status=Payment.INITIATED,
            type=Payment.FOR_TOP_UP_WALLET,
            created_at=timezone.now()
        )
        payment.mark_as_pending(user=user)

        service = WalletTopUpRequestService(
            user=user,
            amount=top_up_amount,
            ip=request.META.get('REMOTE_ADDR'),
            agent=request.META.get('HTTP_USER_AGENT')
        )

        try:
            service.execute()
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        callback_url = SERVER_URL + reverse('financial_management:zarinpal_top_up_wallet_callback')
        gateway = ZarinpalGateway(
            amount=top_up_amount,
            description=f'شارژ کیف پول {user.name}',
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


class ZarinpalTopUpWalletCallbackApiView(APIView):

    def get(self, request):
        authority = request.query_params.get('Authority')
        callback_status = request.query_params.get('Status')

        if callback_status != 'OK':
            return Response({'detail': 'payment failed'}, status=status.HTTP_400_BAD_REQUEST)
        payment = get_object_or_404(Payment, reference_id=authority)

        gateway = ZarinpalGateway(
            amount=payment.amount,
            description=f'شارژ کیف پول {payment.user}',
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
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT'),
                extra_info={"amount": str(payment.amount)}
            )

            service = WalletTopUpService(
                user=payment.user,
                amount=payment.amount,
                ip=request.META.get('REMOTE_ADDR'),
                agent=request.META.get('HTTP_USER_AGENT')
            )

            try:
                service.execute()
            except Exception as e:
                return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

            return Response({'detail': 'payment verify and wallet top up was successfully',
                             'ref_id': result['data']['ref_id']},
                            status=status.HTTP_200_OK)
        else:
            payment.mark_as_failed_payment(user=payment.user)
            FinancialLogger.log(
                user=payment.user,
                action=AuditAction.PAYMENT_FAILED,
                severity=AuditSeverity.INFO,
                payment=payment,
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT'),
                extra_info={"amount": str(payment.amount)}
            )

            return Response({'detail': 'payment verify failed'}, status=status.HTTP_400_BAD_REQUEST)
