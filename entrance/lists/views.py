from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated

from entrance.lists.filters import EntrancePackageFilter
from entrance.models import EntrancePackage
from entrance.serializers import EntrancePackageListSerializer
from helpers.auth import BasicCRUDPermission
from rest_framework import generics


class EntrancePackageListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, BasicCRUDPermission)
    permission_codename = "get.entrance_packages"

    serializer_class = EntrancePackageListSerializer

    pagination_class = LimitOffsetPagination

    ordering_fields = '__all__'
    filterset_class = EntrancePackageFilter
    search_fields = EntrancePackageFilter.Meta.fields.keys()

    def get_queryset(self):
        return EntrancePackage.objects.hasAccess('get').all()
