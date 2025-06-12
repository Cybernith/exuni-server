from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
import base64
import uuid
from django.core.files.base import ContentFile

from affiliate.views import get_business_from_request
from entrance.models import StoreReceiptItem
from entrance.serializers import StoreReceiptItemSerializer
from financial_management.models import Discount
from helpers.auth import BasicObjectPermission
from rest_framework.views import APIView
from django.http import Http404

from rest_framework.response import Response
from rest_framework import status, viewsets

from products.models import Brand, Avail, ProductProperty, Category, Product, ProductGallery, ProductPriceHistory, \
    Feature, Categorization
from products.serializers import BrandSerializer, AvailSerializer, ProductPropertySerializer, CategorySerializer, \
    ProductSerializer, ProductGallerySerializer, BrandLogoUpdateSerializer, CategoryPictureUpdateSerializer, \
    ProductSimpleSerializer, ProductContentDevelopmentSerializer, ProductPictureUpdateSerializer, \
    ProductPriceHistorySerializer, AvailTreeSerializer, AvailTreeRootSerializer, FeatureTreeRootSerializer, \
    CategorizationRootSerializer

from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import generics
from helpers.models import manage_files
from django.db.models import QuerySet, Q

from shop.api_serializers import DiscountSerializer


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


class AvailSubtreeView(APIView):
    def get(self, request, pk):
        root = get_object_or_404(Avail.objects.only('id', 'name', 'parent_id'), pk=pk)

        avails = Avail.objects.all().only('id', 'name', 'parent_id')

        avail_map = {}
        for avail in avails:
            avail_map.setdefault(avail.parent_id, []).append({
                'id': avail.id,
                'name': avail.name,
                'explanation': avail.explanation,
                'image': 'http://exuni.shop' + avail.image.url if avail.image else None,
                'children': []
            })

        def build_tree(parent_id):
            nodes = []
            for cat in avail_map.get(parent_id, []):
                cat['children'] = build_tree(cat['id'])
                nodes.append(cat)
            return nodes

        tree = {
            'id': root.id,
            'name': root.name,
            'explanation': root.explanation,
            'image': 'http://exuni.shop' + root.image.url if root.image else None,
            'children': build_tree(root.id)
        }

        return Response(tree, status=status.HTTP_200_OK)


class AvailTreeSaveView(APIView):
    @transaction.atomic
    def post(self, request):
        data = request.data
        root = self._create_or_update_node(data, parent=None)
        return Response({'success': True, 'root_id': root.id}, status=status.HTTP_200_OK)

    def _create_or_update_node(self, data, parent):
        raw_id = data.get('id')
        name = data['name']
        image_data = data.get('image', None)
        explanation = data.get('explanation', '')

        instance = None
        if self._is_valid_id(raw_id):
            try:
                instance = Avail.objects.get(pk=raw_id)
                instance.name = name
                instance.explanation = explanation
                instance.parent = parent
                if image_data:
                    self._save_image(instance, image_data)
                else:
                    instance.image = None
                    instance.save()
            except Avail.DoesNotExist:
                instance = Avail.objects.create(
                    name=name,
                    explanation=explanation,
                    parent=parent
                )
                if image_data:
                    self._save_image(instance, image_data)
                else:
                    instance.image = None

        else:
            instance = Avail.objects.create(
                name=name,
                explanation=explanation,
                parent=parent
            )
            if image_data:
                self._save_image(instance, image_data)
            else:
                instance.image = None

        children = data.get('children', [])
        current_child_ids = set()
        for child_data in children:
            child_instance = self._create_or_update_node(child_data, parent=instance)
            current_child_ids.add(child_instance.id)

        existing_child_ids = set(instance.children.values_list('id', flat=True))
        to_delete_ids = existing_child_ids - current_child_ids
        if to_delete_ids:
            Avail.objects.filter(id__in=to_delete_ids).delete()

        return instance

    def _is_valid_id(self, val):
        try:
            val = int(val)
            return val > 0
        except (ValueError, TypeError):
            return False

    def _save_image(self, instance, image_data):
        if image_data.startswith("data:image"):
            format, imgstr = image_data.split(';base64,')
            ext = format.split('/')[-1]
            name = f"{uuid.uuid4()}.{ext}"
            decoded_image = base64.b64decode(imgstr)
            content_file = ContentFile(decoded_image, name)
            instance.image.save(name, content_file, save=True)
        else:
            pass


class AvailRootListView(APIView):
    def get(self, request):
        roots = Avail.objects.filter(parent__isnull=True).order_by('id')
        serializer = AvailTreeRootSerializer(roots, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AvailDeleteView(APIView):

    def get_object(self, pk):
        try:
            return Avail.objects.get(pk=pk)
        except Avail.DoesNotExist:
            raise Http404

    def delete(self, request, pk):
        query = self.get_object(pk)
        query.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class FeatureSubtreeView(APIView):

    def get(self, request, pk):
        root = get_object_or_404(Feature.objects.only('id', 'name', 'parent_id'), pk=pk)

        features = Feature.objects.all().only('id', 'name', 'parent_id')

        feature_map = {}
        for feature in features:
            feature_map.setdefault(feature.parent_id, []).append({
                'id': feature.id,
                'name': feature.name,
                'explanation': feature.explanation,
                'image': 'http://exuni.shop' + feature.image.url if feature.image else None,
                'children': []
            })

        def build_tree(parent_id):
            nodes = []
            for cat in feature_map.get(parent_id, []):
                cat['children'] = build_tree(cat['id'])
                nodes.append(cat)
            return nodes

        tree = {
            'id': root.id,
            'name': root.name,
            'explanation': root.explanation,
            'image': 'http://exuni.shop' + root.image.url if root.image else None,
            'children': build_tree(root.id)
        }

        return Response(tree, status=status.HTTP_200_OK)


class FeatureTreeSaveView(APIView):
    @transaction.atomic
    def post(self, request):
        data = request.data
        root = self._create_or_update_node(data, parent=None)
        return Response({'success': True, 'root_id': root.id}, status=status.HTTP_200_OK)

    def _create_or_update_node(self, data, parent):
        raw_id = data.get('id')
        name = data['name']
        image_data = data.get('image', None)
        explanation = data.get('explanation', '')

        instance = None
        if self._is_valid_id(raw_id):
            try:
                instance = Feature.objects.get(pk=raw_id)
                instance.name = name
                instance.explanation = explanation
                instance.parent = parent
                if image_data:
                    self._save_image(instance, image_data)
                else:
                    instance.image = None
                    instance.save()
            except Feature.DoesNotExist:
                instance = Feature.objects.create(
                    name=name,
                    explanation=explanation,
                    parent=parent
                )
                if image_data:
                    self._save_image(instance, image_data)
                else:
                    instance.image = None

        else:
            instance = Feature.objects.create(
                name=name,
                explanation=explanation,
                parent=parent
            )
            if image_data:
                self._save_image(instance, image_data)
            else:
                instance.image = None

        children = data.get('children', [])
        current_child_ids = set()
        for child_data in children:
            child_instance = self._create_or_update_node(child_data, parent=instance)
            current_child_ids.add(child_instance.id)

        existing_child_ids = set(instance.children.values_list('id', flat=True))
        to_delete_ids = existing_child_ids - current_child_ids
        if to_delete_ids:
            Feature.objects.filter(id__in=to_delete_ids).delete()

        return instance

    def _is_valid_id(self, val):
        try:
            val = int(val)
            return val > 0
        except (ValueError, TypeError):
            return False

    def _save_image(self, instance, image_data):
        if image_data.startswith("data:image"):
            format, imgstr = image_data.split(';base64,')
            ext = format.split('/')[-1]
            name = f"{uuid.uuid4()}.{ext}"
            decoded_image = base64.b64decode(imgstr)
            content_file = ContentFile(decoded_image, name)
            instance.image.save(name, content_file, save=True)
        else:
            pass


class FeatureRootListView(APIView):
    def get(self, request):
        roots = Feature.objects.filter(parent__isnull=True).order_by('id')
        serializer = FeatureTreeRootSerializer(roots, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class FeatureDeleteView(APIView):

    def get_object(self, pk):
        try:
            return Feature.objects.get(pk=pk)
        except Feature.DoesNotExist:
            raise Http404

    def delete(self, request, pk):
        query = self.get_object(pk)
        query.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CategorizationSubtreeView(APIView):

    def get(self, request, pk):
        root = get_object_or_404(Categorization.objects.only('id', 'name', 'parent_id'), pk=pk)

        categorizations = Categorization.objects.all().only('id', 'name', 'parent_id')

        categorization_map = {}
        for categorization in categorizations:
            categorization_map.setdefault(categorization.parent_id, []).append({
                'id': categorization.id,
                'name': categorization.name,
                'explanation': categorization.explanation,
                'image': 'http://exuni.shop' + categorization.image.url if categorization.image else None,
                'children': []
            })

        def build_tree(parent_id):
            nodes = []
            for cat in categorization_map.get(parent_id, []):
                cat['children'] = build_tree(cat['id'])
                nodes.append(cat)
            return nodes

        tree = {
            'id': root.id,
            'name': root.name,
            'explanation': root.explanation,
            'image': 'http://exuni.shop' + root.image.url if root.image else None,
            'children': build_tree(root.id)
        }

        return Response(tree, status=status.HTTP_200_OK)


class CategorizationTreeSaveView(APIView):
    @transaction.atomic
    def post(self, request):
        data = request.data
        root = self._create_or_update_node(data, parent=None)
        return Response({'success': True, 'root_id': root.id}, status=status.HTTP_200_OK)

    def _create_or_update_node(self, data, parent):
        raw_id = data.get('id')
        name = data['name']
        image_data = data.get('image', None)
        explanation = data.get('explanation', '')

        instance = None
        if self._is_valid_id(raw_id):
            try:
                instance = Categorization.objects.get(pk=raw_id)
                instance.name = name
                instance.explanation = explanation
                instance.parent = parent
                if image_data:
                    self._save_image(instance, image_data)
                else:
                    instance.image = None
                    instance.save()
            except Categorization.DoesNotExist:
                instance = Categorization.objects.create(
                    name=name,
                    explanation=explanation,
                    parent=parent
                )
                if image_data:
                    self._save_image(instance, image_data)
                else:
                    instance.image = None

        else:
            instance = Categorization.objects.create(
                name=name,
                explanation=explanation,
                parent=parent
            )
            if image_data:
                self._save_image(instance, image_data)
            else:
                instance.image = None

        children = data.get('children', [])
        current_child_ids = set()
        for child_data in children:
            child_instance = self._create_or_update_node(child_data, parent=instance)
            current_child_ids.add(child_instance.id)

        existing_child_ids = set(instance.children.values_list('id', flat=True))
        to_delete_ids = existing_child_ids - current_child_ids
        if to_delete_ids:
            Categorization.objects.filter(id__in=to_delete_ids).delete()

        return instance

    def _is_valid_id(self, val):
        try:
            val = int(val)
            return val > 0
        except (ValueError, TypeError):
            return False

    def _save_image(self, instance, image_data):
        if image_data.startswith("data:image"):
            format, imgstr = image_data.split(';base64,')
            ext = format.split('/')[-1]
            name = f"{uuid.uuid4()}.{ext}"
            decoded_image = base64.b64decode(imgstr)
            content_file = ContentFile(decoded_image, name)
            instance.image.save(name, content_file, save=True)
        else:
            pass


class CategorizationRootListView(APIView):
    def get(self, request):
        roots = Categorization.objects.filter(parent__isnull=True).order_by('id')
        serializer = CategorizationRootSerializer(roots, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CategorizationDeleteView(APIView):

    def get_object(self, pk):
        try:
            return Categorization.objects.get(pk=pk)
        except Categorization.DoesNotExist:
            raise Http404

    def delete(self, request, pk):
        query = self.get_object(pk)
        query.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
