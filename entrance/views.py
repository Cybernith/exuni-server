from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from rest_framework import generics
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from entrance.models import EntrancePackage, EntrancePackageItem, StoreReceipt
from entrance.serializers import EntrancePackageSerializer, EntrancePackageRetrieveSerializer, StoreReceiptSerializer, \
    StoreReceiptItemSerializer, StoreReceiptRetrieveSerializer, EntrancePackageItemSerializer
from helpers.auth import BasicCRUDPermission
from helpers.views.MassRelatedCUD import MassRelatedCUD


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


