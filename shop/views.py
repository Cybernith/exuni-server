import datetime
import hmac
import hashlib
from urllib.parse import urljoin

import requests

from django.db import transaction
from django.db.models import Q, F
from django.http import Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.urls import reverse
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView

from rest_framework.response import Response
from rest_framework import status

from helpers.auth import BasicObjectPermission
from helpers.functions import get_current_user
from products.models import Product
from server.settings import TRUSTED_GATEWAY_IP, GATEWAY_SECRET_PAYMENT_TOKEN, SECRET_KEY
from shop.helpers import reduce_inventory
from shop.models import Cart, WishList, Comparison, ShipmentAddress, LimitedTimeOffer, Rate, Comment, ShopOrder, \
    ShopOrderItem, ShopOrderStatusHistory, Payment
from shop.serializers import CartCRUDSerializer, CartRetrieveSerializer, WishListRetrieveSerializer, \
    WishListCRUDSerializer, ComparisonRetrieveSerializer, ComparisonCRUDSerializer, ShipmentAddressCRUDSerializer, \
    ShipmentAddressRetrieveSerializer, LimitedTimeOfferItemsSerializer, LimitedTimeOfferSerializer, RateSerializer, \
    RateRetrieveSerializer, PostCommentSerializer, CommentSerializer, ShopOrderStatusHistorySerializer
from shop.zarinpal import ZarinpalGateway


class CurrentUserCartApiView(APIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)
    permission_basename = 'cart'

    def get(self, request):
        customer = get_current_user()
        query = Cart.objects.filter(customer=customer)
        serializers = CartRetrieveSerializer(query, many=True, context={'request': request})
        return Response(serializers.data, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.data
        data['customer'] = get_current_user().id
        serializer = CartCRUDSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CartDetailView(APIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)
    permission_basename = 'cart'

    def get_object(self, pk):
        try:
            return Cart.objects.get(pk=pk)
        except Cart.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        query = self.get_object(pk)
        serializers = CartRetrieveSerializer(query)
        return Response(serializers.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        query = self.get_object(pk)
        data = request.data
        data['customer'] = get_current_user().id
        serializer = CartCRUDSerializer(query, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        query = self.get_object(pk)
        query.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CurrentUserWishListApiView(APIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)
    permission_basename = 'wish_list'

    def get(self, request):
        customer = get_current_user()
        query = WishList.objects.filter(customer=customer)
        serializers = WishListRetrieveSerializer(query, many=True, context={'request': request})
        return Response(serializers.data, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.data
        data['customer'] = get_current_user().id
        serializer = WishListCRUDSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WishListDetailView(APIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)
    permission_basename = 'wish_list'

    def get_object(self, pk):
        try:
            return WishList.objects.get(pk=pk)
        except WishList.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        query = self.get_object(pk)
        serializers = WishListRetrieveSerializer(query)
        return Response(serializers.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        query = self.get_object(pk)
        data = request.data
        data['customer'] = get_current_user().id
        serializer = WishListCRUDSerializer(query, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        query = self.get_object(pk)
        query.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CurrentUserComparisonApiView(APIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)
    permission_basename = 'comparison'

    def get(self, request):
        customer = get_current_user()
        query = Comparison.objects.filter(customer=customer)
        serializers = ComparisonRetrieveSerializer(query, many=True, context={'request': request})
        return Response(serializers.data, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.data
        data['customer'] = get_current_user().id
        serializer = ComparisonCRUDSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ComparisonDetailView(APIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)
    permission_basename = 'comparison'

    def get_object(self, pk):
        try:
            return Comparison.objects.get(pk=pk)
        except Comparison.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        query = self.get_object(pk)
        serializers = ComparisonRetrieveSerializer(query)
        return Response(serializers.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        query = self.get_object(pk)
        data = request.data
        data['customer'] = get_current_user().id
        serializer = ComparisonCRUDSerializer(query, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        query = self.get_object(pk)
        query.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CurrentUserShipmentAddressApiView(APIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)
    permission_basename = 'shipment_address'

    def get(self, request):
        customer = get_current_user()
        query = ShipmentAddress.objects.filter(customer=customer)
        serializers = ShipmentAddressRetrieveSerializer(query, many=True, context={'request': request})
        return Response(serializers.data, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.data
        data['customer'] = get_current_user().id
        serializer = ShipmentAddressCRUDSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ShipmentAddressDetailView(APIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)
    permission_basename = 'shipment_address'

    def get_object(self, pk):
        try:
            return ShipmentAddress.objects.get(pk=pk)
        except ShipmentAddress.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        query = self.get_object(pk)
        serializers = ShipmentAddressRetrieveSerializer(query)
        return Response(serializers.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        query = self.get_object(pk)
        data = request.data
        data['customer'] = get_current_user().id
        serializer = ShipmentAddressCRUDSerializer(query, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        query = self.get_object(pk)
        query.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CurrentLimitedTimeOfferRetrieveView(APIView):

    def get(self, request):
        now = datetime.datetime.now()
        query = LimitedTimeOffer.objects.filter(
            Q(to_date_time__lte=now) & Q(from_date_time__gte=now)).select_related('items')
        serializers = LimitedTimeOfferSerializer(query, many=True, context={'request': request})
        return Response(serializers.data, status=status.HTTP_200_OK)


class ProductRateApiView(APIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)
    permission_basename = 'rate'

    def post(self, request):
        data = request.data
        data['customer'] = get_current_user().id
        serializer = RateSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductRateDetailView(APIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)
    permission_basename = 'rate'

    def get_object(self, pk):
        try:
            return Rate.objects.get(pk=pk)
        except Rate.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        query = self.get_object(pk)
        serializers = RateRetrieveSerializer(query)
        return Response(serializers.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        query = self.get_object(pk)
        data = request.data
        data['customer'] = get_current_user().id
        serializer = RateSerializer(query, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        query = self.get_object(pk)
        query.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PostCommentApiView(APIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)
    permission_basename = 'comment'

    def post(self, request):
        data = request.data
        data['customer'] = get_current_user().id
        serializer = PostCommentSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentDetailView(APIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)
    permission_basename = 'comment'

    def get_object(self, pk):
        try:
            return Comment.objects.get(pk=pk)
        except Comment.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        query = self.get_object(pk)
        serializers = CommentSerializer(query)
        return Response(serializers.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        query = self.get_object(pk)
        data = request.data
        data['customer'] = get_current_user().id
        serializer = CommentSerializer(query, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        query = self.get_object(pk)
        query.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShopOrderRegistrationView(APIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)
    permission_basename = 'shop_order'

    def post(self, request):
        data = request.data
        customer = get_current_user()
        cart_items = Cart.objects.filter(customer=customer).select_related('product')
        if not cart_items.exists():
            return Response({'detail': 'your cart is empty'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():

                #Preventing  race condition
                product_ids = [item.product.id for item in cart_items]
                locked_products = Product.objects.filter(id__in=product_ids).select_for_update()

                product_map = {product.id: product for product in locked_products}

                shop_order = ShopOrder.objects.create(
                    customer=customer,
                    date_time=datetime.datetime.now(),
                    shipment_address=data['address'],
                )

                for item in cart_items:
                    product = product_map[item.product.id]
                    if product.inventory < item.quantity:
                        raise Exception('not enough inventory for {}'.format(product.name))

                    ShopOrderItem.objects.create(
                        shop_order=shop_order,
                        product=item.product,
                        price=item.product.last_price,
                        product_quantity=item.quantity,
                    )

                    # Inventory reduction
                    reduce_inventory(item.product.id, item.quantity)

                cart_items.delete()
                shop_order.set_constants()
                return Response(
                    {
                        'detail': 'initial order registration completed',
                        'order_id': shop_order.exuni_tracking_code,
                        'exuni_tracking_code': shop_order.exuni_tracking_code
                    }, status=status.HTTP_201_CREATED)

        except Exception as exception:
            return Response({'detail': str(exception)}, status=status.HTTP_400_BAD_REQUEST)


class ShopOrderStatusHistoryApiView(APIView):
    permission_classes = (IsAuthenticated)

    def get_objects(self, pk, customer):
        try:
            order = ShopOrder.objects.get(id=pk, customer=customer)
            return ShopOrderStatusHistory.objects.filter(shop_order=order)
        except ShopOrderStatusHistory.DoesNotExist:
            raise Http404

    def get(self, request, order_id):
        query = self.get_objects(order_id, request.user)
        serializers = ShopOrderStatusHistorySerializer(query, many=True)
        return Response(serializers.data, status=status.HTTP_200_OK)


class StartPaymentApiView(APIView):

    def post(self, request, order_id):
        order = get_object_or_404(ShopOrder, id=order_id, customer=request.user)

        if hasattr(order, 'payment'):
            return Response({'detail': 'this order already have open payment'}, status=status.HTTP_400_BAD_REQUEST)

        gateway_name = 'gateway'

        payment = Payment.objects.create(
            order=order,
            customer=request.user,
            amount=order.total_price,
            gateway=gateway_name,
            status=Payment.INITIATED
        )

        payment.mark_as_pending(user=request.user)
        gateway_url = f'https://gateway.com/pay?payment_id={payment.id}'

        return Response( {
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
            payment.mark_as_success_payment(user=payment.customer)
            payment.order.mark_as_paid(user=payment.customer)

            return Response({'detail': 'payment verify was successfully'}, status=status.HTTP_201_CREATED)

        else:
            payment.mark_as_failed_payment(user=payment.customer)
            return Response({'detail': 'transaction verify failed'}, status=status.HTTP_400_BAD_REQUEST)


class StartZarinpalPaymentApiView(APIView):
    permission_classes = (IsAuthenticated)

    def post(self, request, order_id):
        order = get_object_or_404(ShopOrder, id=order_id, customer=request.user)

        if hasattr(order, 'payment'):
            return Response({'detail': 'this order already have open payment'}, status=status.HTTP_400_BAD_REQUEST)

        payment = Payment.objects.create(
            order=order,
            customer=request.user,
            amount=order.total_price,
            gateway='zarinpal',
            status=Payment.INITIATED
        )

        payment.mark_as_pending(user=request.user)
        relative_url = reverse('zarinpal_callback')

        gateway = ZarinpalGateway(
            amount=order.total_price,
            description=f'پرداخت سفارش {order.id}',
            callback_url=urljoin(request.build_absolute_url('/'), relative_url)
        )

        try:
            result = gateway.request_payment()
            payment.reference_id = result['authority']
            payment.save()
            return Response({'payment_url': result['payment_url']})

        except Exception as exception:
            return Response({'detail': str(exception)}, status=status.HTTP_400_BAD_REQUEST)


class ZarinpalCallbackApiView(APIView):

    def get(self, request):
        authority = request.query_params.get('Authority')
        status = request.query_params.get('Status')

        if status != 'OK':
            return Response({'detail': 'payment failed'}, status=status.HTTP_400_BAD_REQUEST)

        payment = get_object_or_404(Payment, reference_id=authority)
        order = payment.order

        gateway = ZarinpalGateway(
            amount=payment.amount,
            description=f'تایید پرداخت سفارش {order.id}',
            callback_url=''
        )

        result = gateway.verify_payment(authority)
        if result.get('data') and result['data'].get('code') == 100:
            payment.mark_as_success_payment(user=payment.customer)
            order.mark_as_paid(user=payment.customer)
            return Response({'detail': 'payment verify was successfully', 'ref_id': result['data']['ref_id']},
                            status=status.HTTP_200_OK)
        else:
            payment.mark_as_failed_payment(user=payment.customer)
            return Response({'detail': 'transaction verify failed'}, status=status.HTTP_400_BAD_REQUEST)


class UserProductRateApiView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, product_id):
        user = get_current_user()
        try:
            rate = Rate.objects.get(customer=user, product_id=product_id).level
        except Rate.DoesNotExist:
            rate = None
        return Response(
            {'product_id': product_id, 'rate': rate},
            status=status.HTTP_200_OK
        )


