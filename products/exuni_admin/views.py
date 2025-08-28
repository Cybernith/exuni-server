from django.db import transaction
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
import json
from helpers.auth import BasicObjectPermission
from products.exuni_admin.serializers import AdminProductSerializer, AdminCreateProductSerializer, ProductOfferSerializer
from products.models import Product, ProductPrice, Brand, Category
from products.serializers import ProductPriceUpdateSerializer


class AdminProductApiView(APIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)
    permission_basename = 'product'

    def get(self, request):
        query = Product.objects.all()
        serializers = AdminProductSerializer(query, many=True, context={'request': request})
        return Response(serializers.data, status=status.HTTP_200_OK)


class AdminProductDetailView(APIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)
    permission_basename = 'product'

    def get_object(self, pk):
        try:
            return Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        query = self.get_object(pk)
        serializers = AdminProductSerializer(query)
        return Response(serializers.data, status=status.HTTP_200_OK)


class ProductCreateUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):

        data = request.data.copy()
        if 'variations' in data:
            data['variations'] = json.loads(data['variations'])

        serializer = AdminCreateProductSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            product = serializer.save()

            return Response(AdminCreateProductSerializer(product).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk, *args, **kwargs):
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response(
                {'detail': 'Product not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Create mutable copy of request data
        data = request.data.copy()

        # Convert string values to proper types
        if 'remove_image' in data:
            data['remove_image'] = data['remove_image'] == 'true'

        if 'deleted_gallery_images' in data:
            try:
                data['deleted_gallery_images'] = json.loads(data['deleted_gallery_images'])
            except (TypeError, json.JSONDecodeError):
                data['deleted_gallery_images'] = []

        # Add the same variations parsing as in post method
        if 'variations' in data and isinstance(data['variations'], str):
            try:
                data['variations'] = json.loads(data['variations'])
            except json.JSONDecodeError:
                return Response(
                    {'variations': 'Invalid JSON format'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        serializer = AdminCreateProductSerializer(
            product,
            data=data,
            partial=True,
            context={'request': request}
        )

        if serializer.is_valid():
            updated_product = serializer.save()
            return Response(AdminCreateProductSerializer(updated_product).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductPriceUpdateAPIView(APIView):
    def post(self, request, product_id):
        serializer = ProductPriceUpdateSerializer(data=request.data)
        if serializer.is_valid():
            regular_price = serializer.validated_data['regular_price']
            price = serializer.validated_data['price']

            product = get_object_or_404(Product, pk=product_id)

            product.regular_price = regular_price
            product.save()

            product_price, created = ProductPrice.objects.get_or_create(product=product)
            product_price.change_price(price, user=request.user, note='API update')

            return Response({
                "regular_price": product.regular_price,
                "price": product_price.price
            }, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ApplyOfferAPIView(APIView):
    def post(self, request):
        serializer = ProductOfferSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        brand_in = serializer.validated_data['brand_in']
        cat_in = serializer.validated_data['cat_in']
        offer_percent = serializer.validated_data['offer_percent']

        if not cat_in and not brand_in:
            return Response({"error": "brand or category needed"}, status=status.HTTP_404_NOT_FOUND)

        products = Product.objects.all()
        if brand_in:
            try:
                brand = Brand.objects.get(id=brand_in)
                products = products.filter(brand=brand)
            except Brand.DoesNotExist:
                return Response({"error": "Brand not found"}, status=status.HTTP_404_NOT_FOUND)

        if cat_in:
            try:
                category = Category.objects.get(id=cat_in)
                products = products.filter(category=category)
            except Category.DoesNotExist:
                return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)

        if not products.exists():
            return Response({"message": "No products found for this brand"}, status=status.HTTP_200_OK)

        with transaction.atomic():
            for product in products:
                if product.regular_price is not None:
                    discounted_price = product.regular_price * (1 - offer_percent / 100)

                    product_price, created = ProductPrice.objects.get_or_create(product=product)
                    product_price.change_price(
                        val=int(discounted_price),
                        note=f"Applied {offer_percent}% offer"
                    )
                    product.update(discount_type=Product.PERCENT, discount_margin=offer_percent, price=discounted_price)
        return Response({"message": f"Offer of {offer_percent}% applied to {products.count()} products."})
