from django.db.models import QuerySet
from django.http import Http404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from rest_framework import generics
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from entrance.models import EntrancePackage, EntrancePackageItem, StoreReceipt, EntrancePackageFileColumn
from entrance.serializers import EntrancePackageSerializer, EntrancePackageRetrieveSerializer, StoreReceiptSerializer, \
    StoreReceiptItemSerializer, StoreReceiptRetrieveSerializer, EntrancePackageItemSerializer, \
    EntrancePackageFileUploadSerializer
from helpers.auth import BasicCRUDPermission, BasicObjectPermission
from helpers.models import manage_files
from helpers.views.MassRelatedCUD import MassRelatedCUD
from rest_framework.parsers import FileUploadParser, MultiPartParser, FormParser

from server.settings import BASE_DIR
import pandas as pd


@method_decorator(csrf_exempt, name='dispatch')
class EntrancePackageCreateView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated, BasicCRUDPermission,)
    permission_basename = 'entrance_package'
    serializer_class = EntrancePackageSerializer

    def get_queryset(self):
        return EntrancePackage.objects.hasAccess(self.request.method)

    def create(self, request, *args, **kwargs):
        user = request.user
        data = request.data
        entrance_packages_data = data.get('item')
        items_data = data.get('items')

        serializer = EntrancePackageSerializer(data=entrance_packages_data)
        if serializer.is_valid():
            serializer.save()

        MassRelatedCUD(
            user,
            items_data.get('items'),
            items_data.get('ids_to_delete'),
            'entrance_package',
            serializer.instance.id,
            EntrancePackageItemSerializer,
            EntrancePackageItemSerializer,
        ).sync()

        serializer.instance.update_values()

        return Response(EntrancePackageRetrieveSerializer(instance=serializer.instance).data,
                        status=status.HTTP_201_CREATED)


class EntrancePackageApiView(APIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)
    permission_basename = 'entrance_package'

    def get(self, request):
        query = EntrancePackage.objects.all()
        serializers = EntrancePackageSerializer(query, many=True, context={'request': request})
        return Response(serializers.data, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.data
        serializer = EntrancePackageSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EntrancePackageDetailView(APIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)
    permission_basename = 'entrance_package'

    def get_object(self, pk):
        try:
            return EntrancePackage.objects.get(pk=pk)
        except EntrancePackage.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        query = self.get_object(pk)
        serializers = EntrancePackageSerializer(query)
        return Response(serializers.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        query = self.get_object(pk)
        serializer = EntrancePackageSerializer(query, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        query = self.get_object(pk)
        query.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class EntrancePackageDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated, BasicCRUDPermission)
    permission_basename = 'entrance_package'
    serializer_class = EntrancePackageSerializer

    def get_queryset(self):
        return EntrancePackage.objects.hasAccess(self.request.method)

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset().prefetch_related(
            'created_by',
            'items',
            'items__product',
            'items__currency',
        )
        entrance_packages = get_object_or_404(queryset, pk=pk)
        serializer = EntrancePackageRetrieveSerializer(entrance_packages)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        user = request.user
        data = request.data
        entrance_packages_data = data.get('item')
        items_data = data.get('items')

        serializer = EntrancePackageSerializer(instance=self.get_object(), data=entrance_packages_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        MassRelatedCUD(
            user,
            items_data.get('items'),
            items_data.get('ids_to_delete'),
            'entrance_package',
            serializer.instance.id,
            EntrancePackageItemSerializer,
            EntrancePackageItemSerializer,
        ).sync()

        serializer.instance.update_values()

        return Response(EntrancePackageRetrieveSerializer(instance=serializer.instance).data, status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name='dispatch')
class StoreReceiptCreateView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated, BasicCRUDPermission,)
    permission_basename = 'store_receipt'
    serializer_class = StoreReceiptSerializer

    def get_queryset(self):
        return StoreReceipt.objects.hasAccess(self.request.method)

    def create(self, request, *args, **kwargs):
        user = request.user
        data = request.data
        store_receipt_data = data.get('item')
        items_data = data.get('items')

        serializer = StoreReceiptSerializer(data=store_receipt_data)
        if serializer.is_valid():
            serializer.save()

        MassRelatedCUD(
            user,
            items_data.get('items'),
            items_data.get('ids_to_delete'),
            'store_receipt',
            serializer.instance.id,
            StoreReceiptItemSerializer,
            StoreReceiptItemSerializer,
        ).sync()
        return Response(StoreReceiptRetrieveSerializer(instance=serializer.instance).data,
                        status=status.HTTP_201_CREATED)


class StoreReceiptDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated, BasicCRUDPermission)
    permission_basename = 'store_receipt'
    serializer_class = StoreReceiptSerializer

    def get_queryset(self):
        return StoreReceipt.objects.hasAccess(self.request.method)

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset().prefetch_related(
            'created_by',
            'items',
            'store_receipt',
            'store',
            'storekeeper',
            'item__product',
            'item__currency',
        )
        store_receipts = get_object_or_404(queryset, pk=pk)
        serializer = StoreReceiptRetrieveSerializer(store_receipts)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        user = request.user
        data = request.data
        store_receipts_data = data.get('item')
        items_data = data.get('items')

        serializer = StoreReceiptSerializer(instance=self.get_object(), data=store_receipts_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        MassRelatedCUD(
            user,
            items_data.get('items'),
            items_data.get('ids_to_delete'),
            'store_receipt',
            serializer.instance.id,
            StoreReceiptItemSerializer,
            StoreReceiptItemSerializer,
        ).sync()

        serializer.instance.update_values()

        return Response(StoreReceiptRetrieveSerializer(instance=serializer.instance).data, status=status.HTTP_200_OK)


class EntrancePackageFileUpdateView(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    permission_basename = 'entrance_package'
    serializer_class = EntrancePackageFileUploadSerializer
    parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self) -> QuerySet:
        return EntrancePackage.objects.filter(id=self.request.data['id'])

    def perform_update(self, serializer: EntrancePackageFileUploadSerializer) -> None:
        manage_files(serializer.instance, self.request.data, ['entrance_file'])
        serializer.save()


class EntrancePackageInsertExcelApiView(APIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)
    permission_basename = 'entrance_package'

    def post(self, request):
        data = request.data
        entrance_packages_columns = data.get('packages_columns')
        entrance_package = data.get('entrance_package')
        entrance_package = EntrancePackage.objects.get(id=entrance_package)

        EntrancePackageFileColumn.objects.filter(entrance_package=entrance_package).delete()
        for column in entrance_packages_columns:
            if column['is_in_case_of_sale']:
                EntrancePackageFileColumn.objects.create(
                    entrance_package=entrance_package,
                    key=column['key'],
                    column_number=column['column_number'],
                    in_case_of_sale_type=column['in_case_of_sale_type']
                )
            else:
                EntrancePackageFileColumn.objects.create(
                    entrance_package=entrance_package,
                    key=column['key'],
                    column_number=column['column_number']
                )

        file_path = entrance_package.entrance_file
        EntrancePackageItem.objects.filter(entrance_package=entrance_package).delete()
        data = pd.read_excel(file_path, skiprows=0).values
        for row in data:
            entrance_package_item = EntrancePackageItem.objects.create(entrance_package=entrance_package)
            for item in EntrancePackageFileColumn.objects.filter(entrance_package=entrance_package):
                if item.key == EntrancePackageFileColumn.PRODUCT_CODE:
                    entrance_package_item.product_code = row[item.column_number - 1]
                elif item.key == EntrancePackageFileColumn.PRODUCT_NAME:
                    entrance_package_item.default_name = row[item.column_number - 1]
                elif item.key == EntrancePackageFileColumn.PRODUCT_PRICE:
                    entrance_package_item.default_price = row[item.column_number - 1]
                elif item.key == EntrancePackageFileColumn.NUMBER_OF_BOXES:
                    entrance_package_item.number_of_box = row[item.column_number - 1]
                elif item.key == EntrancePackageFileColumn.NUMBER_OF_PRODUCTS_PER_BOX:
                    entrance_package_item.number_of_products_per_box = row[item.column_number - 1]
                elif item.key == EntrancePackageFileColumn.SIXTEEN_DIGIT_CODE:
                    entrance_package_item.sixteen_digit_code = row[item.column_number - 1]
                elif item.key == EntrancePackageFileColumn.PRICE_IN_CASE_OF_SALE:
                    entrance_package_item.price_in_case_of_sale = row[item.column_number - 1]
                    entrance_package_item.in_case_of_sale_type = item.in_case_of_sale_type
                elif item.key == EntrancePackageFileColumn.BARCODE:
                    entrance_package_item.barcode = row[item.column_number - 1]
            entrance_package_item.save()

        entrance_package.is_inserted = True
        return Response({'msg': 'success'}, status=status.HTTP_201_CREATED)


