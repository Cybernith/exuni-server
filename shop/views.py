import datetime

from urllib.parse import urljoin

import requests

from django.db import transaction
from django.db.models import Q, F
from django.http import Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.timezone import now
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView

from rest_framework.response import Response
from rest_framework import status, generics, viewsets

from financial_management.loggers.financial_logger import FinancialLogger
from financial_management.models import Payment, Transaction, AuditAction, AuditSeverity
from helpers.auth import BasicObjectPermission
from helpers.functions import get_current_user
from products.models import Product
from shop.api_serializers import ApiCartRetrieveSerializer, ApiWishListRetrieveSerializer, \
    ApiComparisonRetrieveSerializer, ApiShipmentAddressRetrieveSerializer, ApiCustomerShopOrderSimpleSerializer, \
    CartAddSerializer, ApiOrderListSerializer, ApiOrderStatusHistorySerializer
from shop.filters import ShopOrderFilter
from shop.helpers import reduce_inventory
from shop.models import Cart, WishList, Comparison, ShipmentAddress, LimitedTimeOffer, Rate, Comment, ShopOrder, \
    ShopOrderItem, ShopOrderStatusHistory
from shop.serializers import CartCRUDSerializer, CartRetrieveSerializer, WishListRetrieveSerializer, \
    WishListCRUDSerializer, ComparisonRetrieveSerializer, ComparisonCRUDSerializer, ShipmentAddressCRUDSerializer, \
    ShipmentAddressRetrieveSerializer, LimitedTimeOfferItemsSerializer, LimitedTimeOfferSerializer, RateSerializer, \
    RateRetrieveSerializer, PostCommentSerializer, CommentSerializer, ShopOrderStatusHistorySerializer, \
    SyncAllDataSerializer, CartInputSerializer, WishlistInputSerializer, CompareItemInputSerializer, \
    ShopOrderSerializer, CustomerShopOrderSimpleSerializer
from shop.throttles import SyncAllDataThrottle, AddToCardRateThrottle, AddToWishListRateThrottle, \
    AddToComparisonRateThrottle, ShopOrderRateThrottle, ToggleWishListBtnRateThrottle, ToggleComparisonBtnRateThrottle, \
    OrderRetrieveThrottle
from subscription.models import DiscountCode
from users.models import User


class CurrentUserCartApiView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [AddToCardRateThrottle]

    def get(self, request):
        customer = get_current_user()
        query = Cart.objects.filter(customer=customer)
        serializers = ApiCartRetrieveSerializer(query, many=True, context={'request': request})
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
    permission_classes = [IsAuthenticated]
    throttle_classes = [AddToCardRateThrottle]

    def get_object(self, pk):
        try:
            query = Cart.objects.get(pk=pk)
            if query.customer != get_current_user():
                raise PermissionError('dont have permission to retrieve this cart')

            return query
        except Cart.DoesNotExist:
            raise Http404

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


class CartSyncView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_scope = 'sync_all_data'

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        user = get_current_user()
        serializer = CartInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        cart_items = validated_data.get('cart_items', [])

        if not cart_items:
            return Response({"message": "No items provided."}, status=status.HTTP_400_BAD_REQUEST)

        cart_items_product_ids = [item['product_id'] for item in cart_items]
        products = Product.objects.filter(id__in=cart_items_product_ids).only('id')
        existing_cart_items = Cart.objects.filter(
            customer=user, product_id__in=cart_items_product_ids
        ).select_related('product')

        existing_cart_map = {item.product_id: item for item in existing_cart_items}
        items_to_create = []
        items_to_update = []

        for item in cart_items:
            product_id = item['product_id']
            quantity = item.get('quantity', 1)

            if product_id not in [product.id for product in products]:
                continue

            if product_id in existing_cart_map:
                cart_item = existing_cart_map[product_id]
                cart_item.quantity += quantity
                items_to_update.append(cart_item)
            else:
                items_to_create.append(
                    Cart(customer=user, product_id=product_id, quantity=quantity)
                )

        if items_to_create:
            Cart.objects.bulk_create(items_to_create, batch_size=100)

        if items_to_update:
            Cart.objects.bulk_update(items_to_update, ['quantity'], batch_size=100)

        return Response({"message": "Cart synced successfully."}, status=status.HTTP_200_OK)


class CurrentUserWishListApiView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [AddToWishListRateThrottle]

    def get(self, request):
        customer = request.user
        query = WishList.objects.filter(customer=customer)
        serializers = ApiWishListRetrieveSerializer(query, many=True, context={'request': request})
        return Response(serializers.data, status=status.HTTP_200_OK)


class WishListDetailView(APIView):
    permission_classes = [IsAuthenticated]
    permission_basename = 'wish_list'

    def get_object(self, pk):
        try:
            return WishList.objects.get(pk=pk)
        except WishList.DoesNotExist:
            raise Http404

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


class WishlistSyncView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_scope = 'sync_all_data'

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        user = request.user
        serializer = WishlistInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        items = validated_data.get('wishlist_items', [])

        if not items:
            return Response({"message": "No items provided."}, status=status.HTTP_400_BAD_REQUEST)

        product_ids = [item['product_id'] for item in items]
        products = Product.objects.filter(id__in=product_ids).only('id')

        existing_wishlist_items = WishList.objects.filter(customer=user, product_id__in=product_ids)
        existing_wishlist_map = {item.product_id: item for item in existing_wishlist_items}

        items_to_create = []

        for item in items:
            product_id = item['product_id']

            if product_id not in [p.id for p in products]:
                continue

            if product_id not in existing_wishlist_map:
                items_to_create.append(
                    WishList(customer=user, product_id=product_id)
                )

        if items_to_create:
            WishList.objects.bulk_create(items_to_create, batch_size=100)

        return Response({"message": "Wishlist synced successfully."}, status=status.HTTP_200_OK)


class ClearCustomerWishListView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [AddToWishListRateThrottle]

    def delete(self, request):
        wish_list = WishList.objects.filter(customer_id=get_current_user())
        wish_list.delete()
        return Response({'message': 'your wish list has been cleared'}, status=status.HTTP_204_NO_CONTENT)


class CurrentUserComparisonApiView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [AddToComparisonRateThrottle]

    def get(self, request):
        customer = get_current_user()
        query = Comparison.objects.filter(customer=customer)
        serializers = ApiComparisonRetrieveSerializer(query, many=True, context={'request': request})
        return Response(serializers.data, status=status.HTTP_200_OK)


class ComparisonDetailView(APIView):
    permission_classes = [IsAuthenticated, BasicObjectPermission]
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


class ComparisonSyncView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_scope = 'sync_all_data'

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        user = get_current_user()
        serializer = CompareItemInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        items = validated_data.get('comparison_items', [])

        if not items:
            return Response({"message": "No items provided"}, status=status.HTTP_400_BAD_REQUEST)

        product_ids = [item['product_id'] for item in items]
        products = Product.objects.filter(id__in=product_ids).only('id')

        existing_comparison_items = Comparison.objects.filter(customer=user, product_id__in=product_ids)
        existing_comparison_map = {item.product_id: item for item in existing_comparison_items}

        items_to_create = []

        for item in items:
            product_id = item['product_id']

            if product_id not in [p.id for p in products]:
                continue

            if product_id not in existing_comparison_map:
                items_to_create.append(
                    Comparison(customer=user, product_id=product_id)
                )

        if items_to_create:
            Comparison.objects.bulk_create(items_to_create, batch_size=100)

        return Response({"message": "Comparison synced successfully."}, status=status.HTTP_200_OK)


class ClearCustomerComparisonView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [AddToComparisonRateThrottle]

    def delete(self, request):
        comparison = Comparison.objects.filter(customer_id=get_current_user())
        comparison.delete()
        return Response({'message': 'your comparisons has been cleared'}, status=status.HTTP_204_NO_CONTENT)


class CurrentUserShipmentAddressApiView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        customer = get_current_user()
        query = ShipmentAddress.objects.filter(customer=customer)
        serializers = ApiShipmentAddressRetrieveSerializer(query, many=True, context={'request': request})
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
    permission_classes = [IsAuthenticated]


    def get_object(self, pk):
        try:
            query = ShipmentAddress.objects.get(pk=pk)
            if query.customer != get_current_user():
                raise PermissionError('dont have permission to retrieve this address')
            return query
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
    permission_classes = [IsAuthenticated]
    throttle_classes = [ShopOrderRateThrottle]

    def post(self, request):
        customer = get_current_user()
        data = request.data
        address_id = data.get('address')
        discount_code_value = data.get('discount_code')

        cart_items = Cart.objects.filter(customer=customer).select_related('product')
        if not cart_items.exists():
            return Response({'message': 'سبد خرید شما خالی است'}, status=status.HTTP_400_BAD_REQUEST)

        if not address_id:
            return Response({'message': 'آدرس الزامی است'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            address = ShipmentAddress.objects.get(id=address_id, customer=customer)
        except ShipmentAddress.DoesNotExist:
            return Response({'message': 'آدرس برای این کاربر معتبر نیست'}, status=status.HTTP_400_BAD_REQUEST)

        discount_code = None
        if discount_code_value:
            try:
                discount_code = DiscountCode.objects.get(code=discount_code_value)
                discount_code.verify()
            except DiscountCode.DoesNotExist:
                return Response({'message': 'کد تخفیف معتبر نمی‌باشد'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                product_ids = list(cart_items.values_list('product_id', flat=True))
                locked_products = Product.objects.filter(id__in=product_ids).select_for_update()
                product_map = {product.id: product for product in locked_products}

                shop_order = ShopOrder.objects.create(
                    customer=customer,
                    date_time=now(),
                    shipment_address=address,
                    discount_code=discount_code,
                )

                order_items = []
                inventory_shortage_info = []

                for item in cart_items:
                    product = product_map[item.product.id]

                    if product.current_inventory.inventory < item.quantity:
                        item.quantity = product.current_inventory.inventory
                        inventory_shortage_info.append(
                            {'name': product.name, 'quantity': product.current_inventory.inventory}
                        )
                    if item.quantity > 0 and product.price > 0:
                        order_items.append(ShopOrderItem(
                            shop_order=shop_order,
                            product=product,
                            price=product.price,
                            product_quantity=item.quantity,
                        ))

                        reduce_inventory(product.id, item.quantity)

                ShopOrderItem.objects.bulk_create(order_items)

                cart_items.delete()
                shop_order.set_constants()
                # handle inventory shortage
                inventory_info = 'ok'
                if len(inventory_shortage_info) > 0:
                    product_inventory_shortage_info = ''
                    for info in inventory_shortage_info:
                        product_inventory_shortage_info += ' - {} برابر {}'.format(info['name'], info['quantity'])
                    inventory_info = 'موجودی کالاهای {} می‌باشد. سبد خرید کاربر با توجه به موجودی فعلی، به‌روزرسانی و ویرایش شد.'.format(product_inventory_shortage_info)

                return Response({
                    'message': 'ثبت اولیه سفارش با موفقیت انجام شد',
                    'order_id': shop_order.id,
                    'inventory_info': inventory_info,
                    'inventory_shortage_info': inventory_shortage_info,
                    'exuni_tracking_code': shop_order.exuni_tracking_code
                }, status=status.HTTP_201_CREATED)

        except ValidationError as validation_error:
            return Response({'message': str(validation_error)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as exception:
            return Response({'message': f'خطا در ثبت سفارش: {str(exception)}'}, status=status.HTTP_400_BAD_REQUEST)


class CustomerOrdersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = ShopOrder.objects.filter(customer=get_current_user()).select_related(
            'shipment_address'
        ).prefetch_related('items', 'history', 'bank_payment')
        serializers = ApiOrderListSerializer(orders, many=True)
        return Response(serializers.data, status=status.HTTP_200_OK)


class CustomerOrdersDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, customer):
        try:
            return ShopOrder.objects.get(id=pk, customer=customer)
        except ShopOrder.DoesNotExist:
            raise Http404

    def get(self, request, order_id):
        order = self.get_object(order_id, customer=get_current_user())
        serializers = ApiOrderListSerializer(order)
        return Response(serializers.data, status=status.HTTP_200_OK)


class ClearCustomerCartView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [AddToCardRateThrottle]

    def delete(self, request):
        carts = Cart.objects.filter(customer_id=get_current_user())
        carts.delete()
        return Response({'message': 'your cart has been cleared'}, status=status.HTTP_204_NO_CONTENT)


class ShopOrderStatusHistoryApiView(APIView):
    permission_classes = [IsAuthenticated]

    def get_objects(self, pk, customer):
        try:
            order = ShopOrder.objects.get(id=pk, customer=customer)
            return ShopOrderStatusHistory.objects.filter(shop_order=order)
        except ShopOrderStatusHistory.DoesNotExist:
            raise Http404

    def get(self, request, order_id):
        query = self.get_objects(order_id, get_current_user())
        serializers = ApiOrderStatusHistorySerializer(query, many=True)
        return Response(serializers.data, status=status.HTTP_200_OK)


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


class SyncAllDataView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_scope = 'sync_all_data'

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        user = get_current_user()

        serializer = SyncAllDataSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        wishlist_items = validated_data.get('wishlist_items', [])
        compare_items = validated_data.get('compare_items', [])
        cart_items = validated_data.get('cart_items', [])

        cart_items_product_ids = [item['product_id'] for item in cart_items]
        products = Product.objects.filter(id__in=cart_items_product_ids).only('id')
        existing_cart_items = Cart.objects.filter(
            customer=user, product_id__in=cart_items_product_ids
        )

        existing_cart_map = {item.product_id: item for item in existing_cart_items}
        cart_items_to_create = []
        cart_items_to_update = []
        for item in cart_items:
            product_id = item['product_id']
            quantity = item.get('quantity', 1)

            if product_id not in [product.id for product in products]:
                continue

            if product_id in existing_cart_map:
                cart_item = existing_cart_map[product_id]
                cart_item.quantity += quantity
                cart_items_to_update.append(cart_item)
            else:
                cart_items_to_create.append(
                    Cart(customer=user, product_id=product_id, quantity=quantity)
                )

        if cart_items_to_create:
            Cart.objects.bulk_create(cart_items_to_create, batch_size=100)

        if cart_items_to_update:
            Cart.objects.bulk_update(cart_items_to_update, ['quantity'], batch_size=100)

        product_ids = set()
        for group in (wishlist_items, compare_items):
            product_ids.update(item['product_id'] for item in group)

        products = Product.objects.filter(id__in=product_ids).only('id')

        existing_wishlist = WishList.objects.filter(customer=user, product_id__in=product_ids)
        existing_compare = Comparison.objects.filter(customer=user, product_id__in=product_ids)

        existing_wishlist_map = {item.product_id: item for item in existing_wishlist}
        existing_compare_map = {item.product_id: item for item in existing_compare}

        wishlist_to_create = []
        compare_to_create = []

        for item in wishlist_items:
            pid = item['product_id']
            if pid in [p.id for p in products] and pid not in existing_wishlist_map:
                wishlist_to_create.append(
                    WishList(customer=user, product_id=pid)
                )

        for item in compare_items:
            pid = item['product_id']
            if pid in [p.id for p in products] and pid not in existing_compare_map:
                compare_to_create.append(
                    Comparison(customer=user, product_id=pid)
                )

        if wishlist_to_create:
            WishList.objects.bulk_create(wishlist_to_create, batch_size=100)
        if compare_to_create:
            Comparison.objects.bulk_create(compare_to_create, batch_size=100)

        return Response({"message": "All data synced successfully."}, status=status.HTTP_200_OK)


class ToggleWishListBTNView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [ToggleWishListBtnRateThrottle]

    def post(self, request):
        data = request.data
        product = get_object_or_404(
            Product,
            pk=data.get('product_id')
        )
        if WishList.objects.filter(
            customer=request.user,
            product=product
        ).exists():
            WishList.objects.get(Q(customer=request.user) & Q(product=product)).delete()
            return Response({'message': 'product deleted from wish list'}, status=status.HTTP_201_CREATED)

        else:
            WishList.objects.create(
                customer=request.user,
                product=product
            )
            return Response({'message': 'product added to wish list'}, status=status.HTTP_201_CREATED)


class ToggleComparisonListBTNView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [ToggleComparisonBtnRateThrottle]

    def post(self, request):
        data = request.data
        product = get_object_or_404(
            Product,
            pk=data.get('product_id')
        )
        if Comparison.objects.filter(
            customer=request.user,
            product=product
        ).exists():
            Comparison.objects.get(Q(customer=request.user) & Q(product=product)).delete()
            return Response({'message': 'product deleted from comparisons'}, status=status.HTTP_201_CREATED)

        else:
            Comparison.objects.create(
                customer=request.user,
                product=product
            )
            return Response({'message': 'product added to comparisons'}, status=status.HTTP_201_CREATED)


class UserOrdersListView(generics.ListAPIView):

    serializer_class = ApiCustomerShopOrderSimpleSerializer
    filterset_class = ShopOrderFilter
    ordering_fields = '__all__'
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return ShopOrder.objects.filter(
            customer=get_current_user()
        ).prefetch_related('history', 'items')


class AddToCartAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CartAddSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data['quantity']
        user = get_current_user()

        cart_item, created = Cart.objects.get_or_create(
            customer=user,
            product_id=product_id,
            defaults={'quantity': quantity}
        )

        if not created:
            cart_item.quantity = quantity
            cart_item.save()

        return Response({
            "message": "محصول با موفقیت به سبد خرید اضافه شد.",
            "item_id": cart_item.id,
            "quantity": cart_item.quantity
        }, status=status.HTTP_200_OK)


class CustomerOrdersSearchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        code = request.query_params.get('code', '').strip()

        orders = ShopOrder.objects.filter(customer=get_current_user())
        orders = orders.filter(Q(exuni_tracking_code__contains=code) | Q(post_tracking_code__contains=code))
        serializers = ApiOrderListSerializer(orders, many=True)
        return Response(serializers.data, status=status.HTTP_200_OK)


class CancelShopOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        shop_order = get_object_or_404(ShopOrder, pk=pk)

        if not (shop_order.customer == get_current_user()):
            return Response(
                {'message': 'دسترسی غیرمجاز'},
                status=status.HTTP_403_FORBIDDEN
            )

        if shop_order.status == ShopOrder.CANCELLED:
            return Response(
                {'message': 'این سفارش از قبل کنسل شده است'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if shop_order.status not in [ShopOrder.PENDING]:
            return Response(
                {'message': 'سفارش فقط در وضعیت در انتظار پرداخت  قابل لغو است'},
                status=status.HTTP_400_BAD_REQUEST
            )

        previous_status = shop_order.status
        shop_order.cancel_order()

        ShopOrderStatusHistory.objects.create(
            shop_order=shop_order,
            previous_status=previous_status,
            new_status=ShopOrder.CANCELLED,
            changed_by=request.user,
            note=request.data.get('note', '')
        )

        try:
            payment = shop_order.bank_payment
        except ShopOrder.bank_payment.RelatedObjectDoesNotExist:
            payment = None

        if payment and payment.status == Payment.SUCCESS:
            exuni_transaction = shop_order.customer.exuni_wallet.increase_balance(
                amount=(payment.amount + payment.used_amount_from_wallet),
                description=f'لغو سفارش {shop_order.exuni_tracking_code} بعد از پرداخت',
                transaction_type=Transaction.ORDER_REFUND,
                order=shop_order,
            )

            FinancialLogger.log(
                user=get_current_user(),
                action=AuditAction.REFUND_PAYMENT_ORDER,
                severity=AuditSeverity.INFO,
                transaction=exuni_transaction,
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT'),
                extra_info={"amount": str(payment.amount)}
            )
            payment.status = Payment.CANCELLED
            payment.save()
        return Response(
            {'status': 'Order cancelled successfully.'},
            status=status.HTTP_200_OK
        )


class OrderMoveToCartAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            order = ShopOrder.objects.prefetch_related('items').get(pk=pk, customer=get_current_user())
        except ShopOrder.DoesNotExist:
            return Response({'message': 'سفارش یافت نشد.'}, status=status.HTTP_404_NOT_FOUND)

        if order.status not in [ShopOrder.PENDING]:
            return Response(
                {'message': 'سفارش فقط در وضعیت در انتظار پرداخت قابل ویرایش است است'},
                status=status.HTTP_400_BAD_REQUEST
            )


        with transaction.atomic():
            order.edit_order()
            for item in order.items.all():
                cart_item, created = Cart.objects.get_or_create(
                    customer=request.user,
                    product=item.product,
                    defaults={'quantity': item.product_quantity}
                )
                if not created:
                    cart_item.quantity += item.product_quantity
                    cart_item.save()

            try:
                payment = order.bank_payment
            except ShopOrder.bank_payment.RelatedObjectDoesNotExist:
                payment = None
            if payment and payment.status == Payment.INITIATED:
                payment.status = 'ca'
                payment.save()

            elif payment and payment.status == Payment.SUCCESS:
                exuni_transaction = order.customer.exuni_wallet.increase_balance(
                    amount=(payment.amount + payment.used_amount_from_wallet),
                    description=f'ویرایش سفارش {order.exuni_tracking_code} بعد از پرداخت',
                    transaction_type=Transaction.ORDER_REFUND,
                    order=order,
                )

                FinancialLogger.log(
                    user=get_current_user(),
                    action=AuditAction.REFUND_PAYMENT_ORDER,
                    severity=AuditSeverity.INFO,
                    transaction=exuni_transaction,
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT'),
                    extra_info={"amount": str(payment.amount)}
                )
                payment.status = Payment.CANCELLED
                payment.save()

            order.delete()

        return Response({'message': 'سفارش با موفقیت حذف و آیتم‌ها به سبد خرید منتقل شدند.'}, status=status.HTTP_200_OK)
