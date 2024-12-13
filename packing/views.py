import datetime

from django.http import Http404
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from helpers.auth import BasicObjectPermission
from helpers.functions import get_current_user
from packing.models import OrderPackage
from packing.serializers import OrderPackageSerializer, OrderPackageSimpleSerializer, OrderPackageItemSerializer
from rest_framework.response import Response
from rest_framework import status

from users.models import User


class OrderPackageApiView(APIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)
    permission_basename = 'order_package'

    def get(self, request):
        query = OrderPackage.objects.all()
        serializers = OrderPackageSerializer(query, many=True, context={'request': request})
        return Response(serializers.data, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.data
        serializer = OrderPackageSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderPackageDetailView(APIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)
    permission_basename = 'order_package'

    def get_object(self, pk):
        try:
            return OrderPackage.objects.get(pk=pk)
        except OrderPackage.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        query = self.get_object(pk)
        serializers = OrderPackageSerializer(query)
        return Response(serializers.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        query = self.get_object(pk)
        serializer = OrderPackageSerializer(query, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        query = self.get_object(pk)
        query.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AddAdminToOrdersApiView(APIView):
    permission_classes = (IsAuthenticated,)
    permission_basename = 'order_package'

    def post(self, request):
        data = request.data
        items = data.get('items', [])
        admin = data.get('admin', None)

        order_packages = OrderPackage.objects.filter(id__in=items)
        order_packages.update(packing_admin=User.objects.get(id=admin))

        return Response({'message': 'admin added succesfully'}, status=status.HTTP_201_CREATED)


class PackedOrderPackagesApiView(APIView):
    permission_classes = (IsAuthenticated,)
    permission_basename = 'order_package'

    def post(self, request):
        data = request.data
        items = data.get('items', [])

        for order in OrderPackage.objects.filter(id__in=items):
            if order.packing_admin != get_current_user():
                raise ValidationError('سفارش {} برای شما نمباشد'.format(order.customer_name))

        order_packages = OrderPackage.objects.filter(id__in=items)
        order_packages.update(is_packaged=True)
        order_packages.update(packing_data_time=datetime.datetime.now())

        return Response({'message': 'packing successfully'}, status=status.HTTP_201_CREATED)


class ShippingOrderPackagesApiView(APIView):
    permission_classes = (IsAuthenticated,)
    permission_basename = 'order_package'

    def post(self, request):
        data = request.data
        items = data.get('items', [])

        for order in OrderPackage.objects.filter(id__in=items):
            if order.packing_admin != get_current_user():
                raise ValidationError('سفارش {} برای شما نمباشد'.format(order.customer_name))

        order_packages = OrderPackage.objects.filter(id__in=items)
        order_packages.update(is_shipped=True)
        order_packages.update(shipping_data_time=datetime.datetime.now())

        return Response({'message': 'shipping successfully'}, status=status.HTTP_201_CREATED)


class GetOrderPackageView(APIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)
    permission_basename = 'order_package'

    def get_object(self, pk):
        try:
            return OrderPackage.objects.get(pk=pk)
        except OrderPackage.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        response = {}
        order_package = self.get_object(pk)

        if order_package.packing_admin != get_current_user() and \
                order_package.business.admin != get_current_user() and \
                get_current_user().user_type not in ['ma', 'stke']:
            raise ValidationError('سفارش {} برای شما نمباشد'.format(order_package.customer_name))

        order_package_serializer = OrderPackageSimpleSerializer(order_package)
        response['order_package'] = order_package_serializer.data
        order_package_items = order_package.items.all().order_by('product__shelf_code')
        order_package_items_serializer = OrderPackageItemSerializer(order_package_items, many=True)

        response['order_package_items'] = order_package_items_serializer.data

        return Response({'response': response}, status=status.HTTP_200_OK)
