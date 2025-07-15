from django.http import Http404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
import json
from helpers.auth import BasicObjectPermission
from products.exuni_admin.serializers import AdminProductSerializer, AdminCreateProductSerializer
from products.models import Product, ProductGallery
from products.serializers import ProductSerializer


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
