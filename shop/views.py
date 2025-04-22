import datetime

from django.db import transaction
from django.db.models import Q, F
from django.http import Http404
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from rest_framework.response import Response
from rest_framework import status

from helpers.auth import BasicObjectPermission
from helpers.functions import get_current_user
from products.models import Product
from shop.helpers import reduce_inventory
from shop.models import Cart, WishList, Comparison, ShipmentAddress, LimitedTimeOffer, Rate, Comment, ShopOrder, \
    ShopOrderItem
from shop.serializers import CartCRUDSerializer, CartRetrieveSerializer, WishListRetrieveSerializer, \
    WishListCRUDSerializer, ComparisonRetrieveSerializer, ComparisonCRUDSerializer, ShipmentAddressCRUDSerializer, \
    ShipmentAddressRetrieveSerializer, LimitedTimeOfferItemsSerializer, LimitedTimeOfferSerializer, RateSerializer, \
    RateRetrieveSerializer, PostCommentSerializer, CommentSerializer


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


