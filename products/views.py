from django.utils import timezone
from rest_framework.permissions import IsAuthenticated

from affiliate.views import get_business_from_request
from entrance.models import StoreReceiptItem
from entrance.serializers import StoreReceiptItemSerializer
from financial_management.models import Discount
from financial_management.serializers import DiscountSerializer
from helpers.auth import BasicObjectPermission
from rest_framework.views import APIView
from django.http import Http404

from rest_framework.response import Response
from rest_framework import status

from products.models import Brand, Avail, ProductProperty, Category, Product, ProductGallery, ProductPriceHistory
from products.serializers import BrandSerializer, AvailSerializer, ProductPropertySerializer, CategorySerializer, \
    ProductSerializer, ProductGallerySerializer, BrandLogoUpdateSerializer, CategoryPictureUpdateSerializer, \
    ProductSimpleSerializer, ProductContentDevelopmentSerializer, ProductPictureUpdateSerializer, \
    ProductPriceHistorySerializer

from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import generics
from helpers.models import manage_files
from django.db.models import QuerySet, Q


class BrandApiView(APIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)
    permission_basename = 'brand'

    def get(self, request):
        query = Brand.objects.all()
        serializers = BrandSerializer(query, many=True, context={'request': request})
        return Response(serializers.data, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.data
        serializer = BrandSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BrandDetailView(APIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)
    permission_basename = 'brand'

    def get_object(self, pk):
        try:
            return Brand.objects.get(pk=pk)
        except Brand.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        query = self.get_object(pk)
        serializers = BrandSerializer(query)
        return Response(serializers.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        query = self.get_object(pk)
        request.data['logo'] = None
        serializer = BrandSerializer(query, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        query = self.get_object(pk)
        query.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BrandLogoUpdateView(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    permission_basename = 'brand'
    serializer_class = BrandLogoUpdateSerializer
    parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self) -> QuerySet:
        return Brand.objects.filter(id=self.request.data['id'])

    def perform_update(self, serializer: BrandLogoUpdateSerializer) -> None:
        manage_files(serializer.instance, self.request.data, ['logo'])
        serializer.save()


class AvailApiView(APIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)
    permission_basename = 'avail'

    def get(self, request):
        query = Avail.objects.all()
        serializers = AvailSerializer(query, many=True, context={'request': request})
        return Response(serializers.data, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.data
        serializer = AvailSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AvailDetailView(APIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)
    permission_basename = 'avail'

    def get_object(self, pk):
        try:
            return Avail.objects.get(pk=pk)
        except Avail.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        query = self.get_object(pk)
        serializers = AvailSerializer(query)
        return Response(serializers.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        query = self.get_object(pk)
        serializer = AvailSerializer(query, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        query = self.get_object(pk)
        query.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductPropertyApiView(APIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)
    permission_basename = 'product_property'

    def get(self, request):
        query = ProductProperty.objects.all()
        serializers = ProductPropertySerializer(query, many=True, context={'request': request})
        return Response(serializers.data, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.data
        serializer =  ProductPropertySerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductPropertyDetailView(APIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)
    permission_basename = 'product_property'

    def get_object(self, pk):
        try:
            return ProductProperty.objects.get(pk=pk)
        except ProductProperty.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        query = self.get_object(pk)
        serializers = ProductPropertySerializer(query)
        return Response(serializers.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        query = self.get_object(pk)
        serializer = ProductPropertySerializer(query, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        query = self.get_object(pk)
        query.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CategoryApiView(APIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)
    permission_basename = 'category'

    def get(self, request):
        query = Category.objects.all()
        serializers = CategorySerializer(query, many=True, context={'request': request})
        return Response(serializers.data, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.data
        serializer = CategorySerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryDetailView(APIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)
    permission_basename = 'category'

    def get_object(self, pk):
        try:
            return Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        query = self.get_object(pk)
        serializers = CategorySerializer(query)
        return Response(serializers.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        query = self.get_object(pk)
        serializer = CategorySerializer(query, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        query = self.get_object(pk)
        query.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CategoryPictureUpdateView(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    permission_basename = 'category'
    serializer_class = CategoryPictureUpdateSerializer
    parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self) -> QuerySet:
        return Category.objects.filter(id=self.request.data['id'])

    def perform_update(self, serializer: CategoryPictureUpdateSerializer) -> None:
        manage_files(serializer.instance, self.request.data, ['logo'])
        serializer.save()


class ProductSimpleApiView(APIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)
    permission_basename = 'product'

    def get(self, request):
        query = Product.objects.all()
        serializers = ProductSimpleSerializer(query, many=True, context={'request': request})
        return Response(serializers.data, status=status.HTTP_200_OK)


class ProductApiView(APIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)
    permission_basename = 'product'

    def get(self, request):
        query = Product.objects.all()
        serializers = ProductSerializer(query, many=True, context={'request': request})
        return Response(serializers.data, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.data
        serializer = ProductSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductDetailView(APIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)
    permission_basename = 'product'

    def get_object(self, pk):
        try:
            return Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        query = self.get_object(pk)
        serializers = ProductSerializer(query)
        return Response(serializers.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        query = self.get_object(pk)
        serializer = ProductSerializer(query, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        query = self.get_object(pk)
        query.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductGalleryApiView(APIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)
    permission_basename = 'product_gallery'

    def get(self, request):
        query = ProductGallery.objects.all()
        serializers = ProductGallerySerializer(query, many=True, context={'request': request})
        return Response(serializers.data, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.data
        serializer = ProductGallerySerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductGalleryDetailView(APIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)
    permission_basename = 'product_gallery'

    def get_object(self, pk):
        try:
            return ProductGallery.objects.get(pk=pk)
        except ProductGallery.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        query = self.get_object(pk)
        serializers = ProductGallerySerializer(query)
        return Response(serializers.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        query = self.get_object(pk)
        serializer = ProductGallerySerializer(query, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        query = self.get_object(pk)
        query.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class GalleryOfProductApiView(APIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)
    permission_basename = 'product_gallery'

    def get_objects(self, pk):
        try:
            return ProductGallery.objects.filter(product=pk, many=True)
        except ProductGallery.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        query = self.get_objects(pk)
        serializers = ProductGallerySerializer(query, many=True)
        return Response(serializers.data, status=status.HTTP_200_OK)


class ProductsStoreReceiptsView(APIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)
    permission_basename = 'store_receipt'

    def get_object(self, pk):
        return StoreReceiptItem.objects.filter(product_id=pk)

    def get(self, request, pk):
        query = self.get_object(pk)
        serializers = StoreReceiptItemSerializer(query, many=True)
        return Response(serializers.data, status=status.HTTP_200_OK)


class NoContentProductsView(APIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)
    permission_basename = 'product'

    def get_object(self, pk):
        return Product.objects.filter(
            Q(picture__isnull=True) |
            Q(explanation__isnull=True) |
            Q(summary_explanation__isnull=True) |
            Q(how_to_use__isnull=True)
        )

    def get(self, request, pk):
        query = self.get_object(pk)
        serializers = ProductSerializer(query, many=True)
        return Response(serializers.data, status=status.HTTP_200_OK)


class ProductContentDevelopmentDetailView(APIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)
    permission_basename = 'product'

    def get_object(self, pk):
        try:
            return Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        query = self.get_object(pk)
        serializers = ProductContentDevelopmentSerializer(query)
        return Response(serializers.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        query = self.get_object(pk)
        serializer = ProductContentDevelopmentSerializer(query, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductPictureUpdateView(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    permission_basename = 'product'
    serializer_class = ProductPictureUpdateSerializer
    parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self) -> QuerySet:
        return Product.objects.filter(id=self.request.data['id'])

    def perform_update(self, serializer: BrandLogoUpdateSerializer) -> None:
        manage_files(serializer.instance, self.request.data, ['picture'])
        serializer.save()


class AffiliateProductAddBusinessView(APIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)
    permission_basename = 'product'

    def put(self, request):
        data = request.data
        business = get_business_from_request(self.request)
        business_products = Product.objects.filter(id__in=data)
        business.products.add(*business_products)
        exclude_products = Product.objects.exclude(id__in=data)
        business.products.remove(*exclude_products)
        return Response({'msg': 'updated'}, status=status.HTTP_201_CREATED)


class ProductPriceHistoryApiView(APIView):
    permission_classes = (IsAuthenticated)

    def get(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise Http404

        query = ProductPriceHistory.objects.filter(prduct=product)
        serializers = ProductPriceHistorySerializer(query, many=True)
        return Response(serializers.data, status=status.HTTP_200_OK)


class ActiveDiscountsAPIView(APIView):

    def get(self, request, *args, **kwargs):
        try:
            now = timezone.now()
            discounts = Discount.objects.filter(
                is_active=True,
                start_date__lte=now,
                end_date__gte=now
            ).select_related('action').prefetch_related(
                'conditions__category_condition__categories',
                'conditions__product_condition__products',
                'conditions__user_condition__users',
                'conditions__brand_condition__brands',
                'conditions__price_over_condition',
                'conditions__price_limit_condition'
            )

            if not discounts.exists():
                return Response({'message': 'هیچ تخفیف فعالی یافت نشد'}, status=200)

            serializer = DiscountSerializer(discounts, many=True)
            return Response(serializer.data)

        except Exception as e:
            return Response({'error': f'خطا در پردازش: {str(e)}'}, status=500)


