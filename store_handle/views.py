from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from helpers.functions import get_current_user
from main.models import Store
from products.models import Product
from store_handle.models import ProductHandleChange, ProductPackingInventoryHandle, ProductStoreInventory
from store_handle.serializers import ProductHandleChangeSerializer, ProductPackingInventoryHandleSerializer, \
    ProductStoreInventorySerializer


class ProductHandleChangeDetailView(APIView):

    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        try:
            result = ProductHandleChange.objects.get(product=product, is_applied=False)
        except ProductHandleChange.DoesNotExist:
            result = None

        if result:
            serializer = ProductHandleChangeSerializer(result)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                {
                    'sixteen_digit_code': product.sixteen_digit_code or None,
                    'name': product.name,
                    'postal_weight': product.postal_weight or None,
                    'length': product.length or None,
                    'width': product.width or None,
                    'height': product.height or None,
                    'aisle': product.aisle or None,
                    'shelf_number': product.shelf_number or None,
                }, status=status.HTTP_200_OK
            )

    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        data = request.data
        serializer = ProductHandleChangeSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            serializer.instance.product = product
            serializer.save(changed_by=get_current_user())
            serializer.instance.apply()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        try:
            result = ProductHandleChange.objects.get(product=product, is_applied=False)
        except ProductHandleChange.DoesNotExist:
            return Http404

        serializer = ProductHandleChangeSerializer(result, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(changed_by=get_current_user())
            serializer.instance.apply()
            serializer.instance.product.packing_handle_done = True
            serializer.instance.product.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductPackingInventoryHandleDetailView(APIView):

    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        store_inventory, created = ProductStoreInventory.objects.get_or_create(
            product=product,
            store=Store.objects.get(code=Store.PACKING),
        )

        serializer = ProductStoreInventorySerializer(store_inventory)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        data = request.data
        serializer = ProductPackingInventoryHandleSerializer(data=data)
        if serializer.is_valid():
            serializer.save(changed_by=get_current_user(), product=product)
            serializer.instance.apply()
            serializer.instance.product.packing_handle_done = True
            serializer.instance.product.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        try:
            result = ProductPackingInventoryHandle.objects.get(product=product, is_applied=False)
        except ProductPackingInventoryHandle.DoesNotExist:
            return Http404

        serializer = ProductPackingInventoryHandleSerializer(result, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(changed_by=get_current_user())
            serializer.instance.apply()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

