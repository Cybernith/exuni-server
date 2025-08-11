from django.http import Http404
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from helpers.functions import get_current_user
from main.models import Store
from products.models import Product
from store_handle.models import ProductHandleChange, ProductPackingInventoryHandle, ProductStoreInventory, \
    ProductStoreInventoryHandle
from store_handle.serializers import ProductHandleChangeSerializer, ProductPackingInventoryHandleSerializer, \
    ProductStoreInventorySerializer, ProductStoreInventoryHandleSerializer, StoreInventoryUpdateSerializer
from rest_framework import generics


class ProductHandleChangeDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        try:
            result = ProductHandleChange.objects.get(product=product, is_applied=False)
        except ProductHandleChange.DoesNotExist:
            result = None

        vars = list(product.variations.all().values('id', 'name', 'sixteen_digit_code', 'picture', 'expired_date',
                                                    'postal_weight', 'length', 'width', 'height', 'shelf_number', 'aisle')
                    )
        for var in vars:
            inventory = ProductStoreInventory.objects.filter(product_id=var['id'], store=Store.objects.get(code=Store.PACKING))
            if inventory.exists():
                inventory = inventory.first()
                var['inventory'] = inventory.inventory
                var['minimum_inventory'] = inventory.minimum_inventory
        if result:
            serializer = ProductHandleChangeSerializer(result)
            data = serializer.data
            data['variations'] = vars
            data['type'] = product.product_type
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response(
                {
                    'image': product.picture.url if product.picture else None,
                    'sixteen_digit_code': product.sixteen_digit_code or None,
                    'name': product.name,
                    'postal_weight': product.postal_weight or None,
                    'length': product.length or None,
                    'width': product.width or None,
                    'height': product.height or None,
                    'aisle': product.aisle or None,
                    'type': product.product_type,
                    'shelf_number': product.shelf_number or None,
                    'expired_date': product.expired_date or None,
                    'variations': vars,
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
    permission_classes = [IsAuthenticated, IsAdminUser]

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
        variations = data['variations']
        for variation in variations:
            variation_packing_inventory_handle = ProductPackingInventoryHandle.objects.create(
                product=Product.objects.get(pk=variation['id']),
                minimum_inventory=variation.get('minimum_inventory', 0),
                inventory=variation.get('inventory', 0),
                changed_by=get_current_user(),
            )
            var = Product.objects.get(pk=variation['id'])

            variation_handle_change = ProductHandleChange.objects.create(
                product=var,
                sixteen_digit_code=variation.get('sixteen_digit_code', var.id),
                name=variation.get('name'),
                shelf_number=variation.get('shelf_number'),
                aisle=variation.get('aisle'),
                height=variation.get('height'),
                width=variation.get('width'),
                length=variation.get('length'),
                expired_date=variation.get('expired_date'),
                postal_weight=variation.get('postal_weight'),
            )
            variation_packing_inventory_handle.apply()
            variation_handle_change.apply()

        del data['variations']
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


class ProductStoreInventoryHandleCreateAPIView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    queryset = ProductStoreInventoryHandle.objects.all()
    serializer_class = ProductStoreInventoryHandleSerializer


class ProductStoreInventoryUpdateAPIView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    queryset = ProductStoreInventoryHandle.objects.all()
    serializer_class = StoreInventoryUpdateSerializer
    lookup_field = 'pk'
