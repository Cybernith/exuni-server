from django.db.models import QuerySet, Q
from django.http import Http404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from rest_framework import generics
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from entrance.models import EntrancePackage, EntrancePackageItem, StoreReceipt, EntrancePackageFileColumn, \
    StoreReceiptItem
from entrance.serializers import EntrancePackageSerializer, EntrancePackageRetrieveSerializer, StoreReceiptSerializer, \
    StoreReceiptItemSerializer, StoreReceiptRetrieveSerializer, EntrancePackageItemSerializer, \
    EntrancePackageFileUploadSerializer
from helpers.auth import BasicCRUDPermission, BasicObjectPermission
from helpers.models import manage_files
from helpers.views.MassRelatedCUD import MassRelatedCUD
from rest_framework.parsers import FileUploadParser, MultiPartParser, FormParser

from main.models import Currency
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
            if column['currency']:
                entrance_package.currency = Currency.objects.get(id=column['currency'])
                entrance_package.save()
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
                    entrance_package_item.product_code = row[item.column_number]
                elif item.key == EntrancePackageFileColumn.PRODUCT_NAME:
                    entrance_package_item.default_name = row[item.column_number]
                elif item.key == EntrancePackageFileColumn.PRODUCT_PRICE:
                    entrance_package_item.default_price = row[item.column_number]
                elif item.key == EntrancePackageFileColumn.NUMBER_OF_BOXES:
                    entrance_package_item.number_of_box = row[item.column_number]
                elif item.key == EntrancePackageFileColumn.NUMBER_OF_PRODUCTS_PER_BOX:
                    entrance_package_item.number_of_products_per_box = row[item.column_number]
                elif item.key == EntrancePackageFileColumn.SIXTEEN_DIGIT_CODE:
                    entrance_package_item.sixteen_digit_code = row[item.column_number]
                elif item.key == EntrancePackageFileColumn.PRICE_IN_CASE_OF_SALE:
                    entrance_package_item.price_in_case_of_sale = row[item.column_number]
                    entrance_package_item.in_case_of_sale_type = item.in_case_of_sale_type
                elif item.key == EntrancePackageFileColumn.BARCODE:
                    entrance_package_item.barcode = row[item.column_number]
                elif item.key == EntrancePackageFileColumn.PRICE_SUM:
                    entrance_package_item.price_sum = row[item.column_number]
                elif item.key == EntrancePackageFileColumn.NUMBER_OF_PRODUCTS:
                    entrance_package_item.number_of_products = row[item.column_number]
            entrance_package_item.save()

        entrance_package.is_inserted = True
        entrance_package.save()

        return Response({'msg': 'success'}, status=status.HTTP_201_CREATED)


class GetTableOfPackageApiView(APIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)
    permission_basename = 'entrance_package'

    def get_object(self, pk):
        try:
            return EntrancePackage.objects.get(pk=pk)
        except EntrancePackage.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        package = self.get_object(pk)

        if not package.entrance_file:
            return Response({'message': 'package file is not available'}, status=status.HTTP_204_NO_CONTENT)

        file_path = package.entrance_file
        data = pd.read_excel(file_path, keep_default_na='').values
        response = {'result': data}
        return Response(response, status=status.HTTP_200_OK)


class PackageDetailView(APIView):
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


class PackageItemDetailView(APIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)
    permission_basename = 'entrance_package_item'

    def get_object(self, pk):
        return EntrancePackageItem.objects.filter(entrance_package_id=pk)

    def get(self, request, pk):
        query = self.get_object(pk)
        serializers = EntrancePackageItemSerializer(query)
        return Response(serializers.data, status=status.HTTP_200_OK)


class UpdatePackageItemsView(APIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)
    permission_basename = 'entrance_package_item'

    def put(self, request):

        data = request.data
        for item in data:
            entrance_package_item = EntrancePackageItem.objects.get(id=item['id'])
            entrance_package_item.product_code = item['product_code']
            entrance_package_item.default_name = item['default_name']
            entrance_package_item.number_of_products_per_box = item['number_of_products_per_box']
            entrance_package_item.number_of_products = item['number_of_products']
            entrance_package_item.number_of_box = item['number_of_box']
            entrance_package_item.default_price = item['default_price']
            entrance_package_item.in_case_of_sale_type = item['in_case_of_sale_type']
            entrance_package_item.price_in_case_of_sale = item['price_in_case_of_sale']
            entrance_package_item.discount_type = item['discount_type']
            entrance_package_item.discount = item['discount']
            entrance_package_item.save()

        return Response({'msg': 'success'}, status=status.HTTP_200_OK)


class RemoveExcelView(APIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)
    permission_basename = 'entrance_package'

    def get_object(self, pk):
        try:
            return EntrancePackage.objects.get(pk=pk)
        except EntrancePackage.DoesNotExist:
            raise Http404

    def delete(self, request, pk):
        query = self.get_object(pk)
        EntrancePackageItem.objects.filter(entrance_package=query).delete()
        EntrancePackageFileColumn.objects.filter(entrance_package=query).delete()
        query.is_inserted = False
        query.entrance_file = None
        query.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


class StorePackagesView(APIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)
    permission_basename = 'entrance_package'

    def get_object(self, pk):
        ids = []
        for package in EntrancePackage.objects.filter(store_id=pk):
            if not package.inserted_to_store:
                ids.append(package.id)
        #return EntrancePackage.objects.filter(id__in=ids)
        return EntrancePackage.objects.filter(store_id=pk)

    def get(self, request, pk):
        query = self.get_object(pk)
        serializers = EntrancePackageSerializer(query, many=True)
        return Response(serializers.data, status=status.HTTP_200_OK)


class StoreReceiptApiView(APIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)
    permission_basename = 'store_receipt'

    def get(self, request):
        query = StoreReceipt.objects.all()
        serializers = StoreReceiptSerializer(query, many=True, context={'request': request})
        return Response(serializers.data, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.data
        serializer = StoreReceiptSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StoreReceiptDetail(APIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)
    permission_basename = 'store_receipt'

    def get_object(self, pk):
        try:
            return StoreReceipt.objects.get(pk=pk)
        except StoreReceipt.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        query = self.get_object(pk)
        serializers = StoreReceiptSerializer(query)
        return Response(serializers.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        query = self.get_object(pk)
        serializer = StoreReceiptSerializer(query, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        query = self.get_object(pk)
        query.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CreateReceiptsItemsView(APIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)
    permission_basename = 'store_receipt_item'

    def post(self, request):
        data = request.data
        store_receipt = data.get('store_receipt')
        store_receipt = StoreReceipt.objects.get(id=store_receipt)
        items = data.get('items')

        for item in items:
            StoreReceiptItem.objects.create(
                store_receipt=store_receipt,
                product_code=item['product_code'],
                default_name=item['default_name'],
                number_of_products_per_box=item['input_product_per_box'],
                number_of_box=item['input_box'],
                new_product_shelf_code=item['new_product_shelf_code'],
                content_production_count=item['content_production_count'],
                failure_count=item['failure_count'],
            )

        return Response({'msg': 'success'}, status=status.HTTP_200_OK)

