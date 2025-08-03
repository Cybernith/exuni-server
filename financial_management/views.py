import datetime
import time
from decimal import Decimal

from django.db.models import Sum
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from financial_management.loggers.financial_logger import FinancialLogger
from financial_management.models import Payment, AuditAction, AuditSeverity, Discount, DiscountAction, Transaction, \
    Wallet
from financial_management.serializers import DiscountResultSerializer
from financial_management.serivces.discount_evaluator import evaluate_discount
from financial_management.serivces.wallet_top_up_service import WalletTopUpRequestService, WalletTopUpService
from financial_management.zarinpal import ZarinpalGateway
from helpers.functions import get_current_user, date_to_str
from products.models import Product
from server.gateway_configs import TRUSTED_GATEWAY_IP, GATEWAY_SECRET_PAYMENT_TOKEN
from server.settings import SERVER_URL, SECRET_KEY, FRONT_URL
from shop.models import ShopOrder
from financial_management.throttles import PaymentRateThrottle
import hmac
from subscription.models import DiscountCode
import hashlib
import json
from django.core.cache import cache

import random
import string


def generate_top_up_wallet_code_with_mobile(mobile_number):
    prefix = "TW"
    random_chars_len = 20 - len(prefix) - len(mobile_number)
    random_chars = ''.join(random.choices(string.ascii_uppercase, k=random_chars_len))
    return prefix + mobile_number + random_chars


def generate_pay_from_wallet_code_with_mobile(mobile_number):
    prefix = "PFW"
    random_chars_len = 20 - len(prefix) - len(mobile_number)
    random_chars = ''.join(random.choices(string.ascii_uppercase, k=random_chars_len))
    return prefix + mobile_number + random_chars


class StartZarinpalPaymentApiView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [PaymentRateThrottle]

    def post(self, request, order_id):

        order = get_object_or_404(ShopOrder, id=order_id, customer=get_current_user())

        payment = getattr(order, 'bank_payment', None)
        if payment and payment.status == 'su':
            return Response({'message': 'this order already have payment'}, status=status.HTTP_400_BAD_REQUEST)
        elif payment and payment.status != 'su':
            payment.status = 'ca'
            payment.save()

        if request.data.get('use_wallet', False):
            transaction_id = generate_pay_from_wallet_code_with_mobile(order.customer.mobile_number)
            payment = order.pay_with_wallet(transaction_id=transaction_id)
            if not payment:
                FinancialLogger.log(
                    user=order.customer,
                    action=AuditAction.PAYMENT_ORDER_FROM_WALLET,
                    severity=AuditSeverity.INFO,
                    transaction=Transaction.objects.get(transaction_id=transaction_id),
                    ip_address=self.kwargs.get("ip"),
                    user_agent=self.kwargs.get("agent"),
                    extra_info={
                        "amount": str(order.final_amount),
                        "order": str(order.id),
                    }
                )

                return Response(
                    {
                        'payment_url': f'/payment/success?status=success&type=wallet&payment_date={date_to_str(datetime.date.today())}&amount={order.final_amount}&order_id={order.id}'
                    }
                )
        else:
            payment = order.pay()

        callback_url = SERVER_URL + reverse('financial_management:zarinpal_callback')

        description = f'پرداخت سفارش {order.id} کاربر {order.customer.mobile_number}'
        if request.data.get('use_wallet', False):
            description = f'پرداخت سفارش {order.id} کاربر {order.customer.mobile_number} مبلغ {payment.used_amount_from_wallet} از کیف پول با شناسه {transaction_id} '

        gateway = ZarinpalGateway(
            amount=payment.payable_amount,
            mobile=payment.shop_order.customer.mobile_number,
            payment_id=order.id,
            description=description,
            callback_url=callback_url
        )

        try:
            result = gateway.request_payment()
            payment.reference_id = result['authority']
            payment.save()
            FinancialLogger.log(
                user=payment.user,
                action=AuditAction.PAYMENT_REQUEST,
                severity=AuditSeverity.INFO,
                payment=payment,
                ip_address=self.kwargs.get("ip"),
                user_agent=self.kwargs.get("agent"),
                extra_info={
                    "amount": str(payment.payable_amount),
                    "authority": result['authority'],
                    "order": str(order.id),
                    "used_from_wallet": str(payment.used_amount_from_wallet),
                }
            )

            return Response({'payment_url': result['payment_url']})

        except Exception as exception:
            payment.delete()
            return Response({'message': str(exception)}, status=status.HTTP_400_BAD_REQUEST)


class ZarinpalCallbackApiView(APIView):

    def get(self, request):
        authority = request.query_params.get('Authority')
        FinancialLogger.log(
            user=None,
            action=AuditAction.MANUAL_ADJUSTMENT,
            severity=AuditSeverity.INFO,
            ip_address=self.kwargs.get("ip"),
            user_agent=self.kwargs.get("agent"),
            extra_info={
                "authority": authority,
                "info": 'callback called',
            }
        )

        callback_status = request.query_params.get('Status')
        try:
            payment = get_object_or_404(Payment, reference_id=authority)
            payment.callback_called = True
            payment.save()
            order = payment.shop_order

        except Exception as e:
            FinancialLogger.log(
                user=None,
                action=AuditAction.MANUAL_ADJUSTMENT,
                severity=AuditSeverity.WARNING,
                ip_address=self.kwargs.get("ip"),
                user_agent=self.kwargs.get("agent"),
                extra_info={
                    "authority": authority,
                    "info": 'error {}'.format(str(e)),
                }
            )
        payment = get_object_or_404(Payment, reference_id=authority)
        order = payment.shop_order
        if callback_status != 'OK':
            payment.mark_as_failed_payment(user=payment.user)
            FinancialLogger.log(
                user=payment.user,
                action=AuditAction.PAYMENT_FAILED,
                severity=AuditSeverity.INFO,
                payment=payment,
                ip_address=self.kwargs.get("ip"),
                user_agent=self.kwargs.get("agent"),
                extra_info={
                    "amount": str(payment.payable_amount),
                    "order": str(order.id),
                    "authority": payment.reference_id,
                }
            )

            return redirect(f'{FRONT_URL}/payment/fail?orderId={order.id}')
        FinancialLogger.log(
            user=payment.user,
            action=AuditAction.MANUAL_ADJUSTMENT,
            severity=AuditSeverity.INFO,
            payment=payment,
            ip_address=self.kwargs.get("ip"),
            user_agent=self.kwargs.get("agent"),
            extra_info={
                "amount": str(payment.payable_amount),
                "order": str(order.id),
                "authority": payment.reference_id,
                "info": 'callback called',
            }
        )

        gateway = ZarinpalGateway(
            amount=payment.payable_amount,
            description=f'تایید پرداخت سفارش {order.id} کاربر {order.customer.mobile_number}',
            callback_url=''
        )
        result = {'data': {'code': 'start'}}
        counter = 0
        while result['data'].get('code') not in [100, 101]:
            if counter != 5:
                result = gateway.verify_payment(authority)
                counter += 1
                time.sleep(counter)

        if result.get('data') and result['data'].get('code') in [100, 101]:
            if payment.used_amount_from_wallet > 0:
                wallet = payment.user.exuni_wallet

                wallet.reduce_balance(
                    transaction_id=payment.transaction_id,
                    amount=payment.used_amount_from_wallet,
                    shop_order=order,
                    description=f"پرداخت قسمتی از مبلغ سفارش {order.id}"
                )

                FinancialLogger.log(
                    user=order.customer,
                    action=AuditAction.PAYMENT_ORDER_FROM_WALLET,
                    severity=AuditSeverity.INFO,
                    transaction=Transaction.objects.get(transaction_id=payment.transaction_id),
                    ip_address=self.kwargs.get("ip"),
                    user_agent=self.kwargs.get("agent"),
                    extra_info={
                        "amount": str(payment.used_amount_from_wallet),
                        "order": str(order.id),
                    }
                )

                wallet.refresh_from_db()
            payment.zarinpal_ref_id = result['data'].get('ref_id')
            payment.card_pan = result['data'].get('card_pan')
            payment.is_verified = True
            payment.save()
            payment.mark_as_success_payment(user=payment.user)
            FinancialLogger.log(
                user=payment.user,
                action=AuditAction.PAYMENT_ORDER,
                severity=AuditSeverity.INFO,
                payment=payment,
                ip_address=self.kwargs.get("ip"),
                user_agent=self.kwargs.get("agent"),
                extra_info={
                    "amount": str(payment.payable_amount),
                    "order": str(order.id),
                    "authority": payment.reference_id,
                }
            )


            if order.discount_code:
                order.discount_code.use()
            order.mark_as_paid()
            return redirect(f'{FRONT_URL}/payment/success?type=gateway&orderId={order.id}')
        else:
            payment.used_amount_from_wallet = 0
            payment.save()
            payment.mark_as_failed_payment(user=payment.user)
            FinancialLogger.log(
                user=payment.user,
                action=AuditAction.PAYMENT_FAILED,
                severity=AuditSeverity.WARNING,
                payment=payment,
                ip_address=self.kwargs.get("ip"),
                user_agent=self.kwargs.get("agent"),
                extra_info={
                    "amount": str(payment.payable_amount),
                    "order": str(order.id),
                    "authority": payment.reference_id,
                    "verify": False,
                }
            )
            return redirect(f'{FRONT_URL}/payment/fail?orderId={order.id}')


class StartPaymentApiView(APIView):
    throttle_classes = [PaymentRateThrottle]

    def post(self, request, order_id):
        order = get_object_or_404(ShopOrder, id=order_id, customer=request.user)

        payment_status = getattr(order, 'bank_payment', None)
        if payment_status and payment_status.status != 'pending':
            return Response({'message': 'this order already have open payment'}, status=status.HTTP_400_BAD_REQUEST)

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
            return Response({'message': 'invalid gateway token'}, status=status.HTTP_403_FORBIDDEN)

        if client_ip not in TRUSTED_GATEWAY_IP:
            return Response({'message': 'Unauthorized IP'}, status=status.HTTP_403_FORBIDDEN)

        if not self.verify_signature(payload, signature, SECRET_KEY):
            return Response({'message': 'invalid gateway signature'}, status=status.HTTP_403_FORBIDDEN)

        payment_id = request.data.get('payment_id')
        success = request.data.get('success')
        payment = get_object_or_404(Payment, id=payment_id)

        if success:
            payment.mark_as_success_payment(user=payment.user)
            payment.shop_order.mark_as_paid()

            return Response({'message': 'payment verify was successfully'}, status=status.HTTP_201_CREATED)

        else:
            payment.mark_as_failed_payment(user=payment.user)
            return Response({'message': 'transaction verify failed'}, status=status.HTTP_400_BAD_REQUEST)


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
            'discount_code': discount_code.code,
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

    def post(self, request):
        user = get_current_user()
        top_up_amount = request.data.get('top_up_amount', None)

        try:
            top_up_amount = int(top_up_amount)
        except (TypeError, ValueError):
            return Response({'message': 'Invalid amount'}, status=status.HTTP_400_BAD_REQUEST)

        if not top_up_amount:
            return Response({'message': 'amount should be positive'},
                            status=status.HTTP_400_BAD_REQUEST)
        transaction_id = generate_top_up_wallet_code_with_mobile(user.mobile_number)
        fee = (round(top_up_amount) / 100 * 0.5) + 350

        payment = Payment.objects.create(
            user=user,
            amount=top_up_amount,
            fee=fee,
            gateway='zarinpal',
            status=Payment.INITIATED,
            type=Payment.FOR_TOP_UP_WALLET,
            transaction_id=transaction_id,
            created_at=timezone.now()
        )
        payment.mark_as_pending(user=user)

        callback_url = SERVER_URL + reverse('financial_management:zarinpal_top_up_wallet_callback')
        gateway = ZarinpalGateway(
            amount=payment.payable_amount,
            description=f'شارژ کیف پول {user.mobile_number}',
            mobile=user.mobile_number,
            payment_id=transaction_id,
            callback_url=callback_url
        )
        try:
            result = gateway.request_payment()
            service = WalletTopUpRequestService(
                user=user,
                amount=top_up_amount,
                authority=result['authority'],
                ip=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT')
            )

            try:
                service.execute()
            except Exception as e:
                return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

            payment.reference_id = result['authority']
            payment.save()
            return Response({'payment_url': result['payment_url']})

        except Exception as exception:
            payment.delete()
            return Response({'message': str(exception)}, status=status.HTTP_400_BAD_REQUEST)


class ZarinpalTopUpWalletCallbackApiView(APIView):

    def get(self, request):
        authority = request.query_params.get('Authority')
        callback_status = request.query_params.get('Status')

        payment = get_object_or_404(Payment, reference_id=authority)

        if callback_status != 'OK':
            payment.mark_as_failed_payment(user=payment.user)
            FinancialLogger.log(
                user=payment.user,
                action=AuditAction.PAYMENT_FAILED,
                severity=AuditSeverity.INFO,
                payment=payment,
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT'),
                extra_info={
                    "amount": str(payment.amount),
                    "authority": payment.reference_id,
                    "type": 'top up wallet',
                }
            )
            return redirect(f'{FRONT_URL}/payment/fail?top_up_wallet=true&amount={payment.amount}')

        gateway = ZarinpalGateway(
            amount=payment.payable_amount,
            description=f'شارژ کیف پول {payment.user}',
            callback_url=''
        )

        result = {'data': {'code': 'start'}}
        counter = 0
        while result['data'].get('code') not in [100, 101]:
            if counter != 3:
                result = gateway.verify_payment(authority)
                counter += 1
                time.sleep(1)

        if result.get('data') and result['data'].get('code') in [100, 101]:
            payment.zarinpal_ref_id = result['data'].get('ref_id')
            payment.card_pan = result['data'].get('card_pan')
            payment.save()
            payment.mark_as_success_payment(user=payment.user)
            FinancialLogger.log(
                user=payment.user,
                action=AuditAction.PAYMENT_FOR_TOP_UP_WALLET,
                severity=AuditSeverity.INFO,
                payment=payment,
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT'),
                extra_info={"amount": str(payment.payable_amount)}
            )

            service = WalletTopUpService(
                user=payment.user,
                amount=payment.amount,
                transaction_id=payment.transaction_id,
                ip=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT')
            )

            try:
                service.execute()
            except Exception as e:
                return redirect(f'{FRONT_URL}/payment/fail?top_up_wallet=true&amount={payment.amount}&message={e}')

            return redirect(f'{FRONT_URL}/payment/success?top_up_wallet=true&amount={payment.amount}')
        else:
            payment.mark_as_failed_payment(user=payment.user)
            FinancialLogger.log(
                user=payment.user,
                action=AuditAction.PAYMENT_FAILED,
                severity=AuditSeverity.WARNING,
                payment=payment,
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT'),
                extra_info={
                    "amount": str(payment.amount),
                    "authority": payment.reference_id,
                    "type": 'top up wallet',
                    "verify": False,
                }
            )
            return redirect(f'{FRONT_URL}/payment/fail?top_up_wallet=true&amount={payment.amount}')



class WalletBalanceSumAPIView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        total_balance = Wallet.objects.all().aggregate(total=Sum('balance'))['total'] or 0
        return Response({'total_balance': total_balance})
