from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from rest_framework import generics
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from entrance.models import EntrancePackage, EntrancePackageItem
from entrance.serializers import EntrancePackageSerializer, EntrancePackageRetrieveSerializer
from helpers.auth import BasicCRUDPermission
from helpers.views.MassRelatedCUD import MassRelatedCUD


@method_decorator(csrf_exempt, name='dispatch')
class EntrancePackageCreateView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated, BasicCRUDPermission,)
    permission_basename = 'entrance_packages'
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
            'entrance_packages',
            serializer.instance.id,
            EntrancePackageItem,
            EntrancePackageItem,
        ).sync()

        serializer.instance.update_values()
        is_confirmed = data.get('_confirmed')
        if not is_confirmed:
            serializer.instance.check_account_balance_confirmations()

        return Response(EntrancePackageRetrieveSerializer(instance=serializer.instance).data,
                        status=status.HTTP_201_CREATED)


class EntrancePackageDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated, BasicCRUDPermission)
    permission_basename = 'entrance_packages'
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
            'entrance_packages',
            serializer.instance.id,
            EntrancePackageItem,
            EntrancePackageItem,
        ).sync()

        serializer.instance.update_values()

        return Response(EntrancePackageRetrieveSerializer(instance=serializer.instance).data, status=status.HTTP_200_OK)


