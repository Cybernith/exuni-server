from helpers.functions import get_current_user
from main.lists.filters import StoreFilter
from main.store_keeping.serializers import StoreKeepingStoreSerializer
from server.store_configs import PACKING_STORE_ID
from main.models import Store
from django.http import Http404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from helpers.auth import BasicObjectPermission
from rest_framework import generics
from rest_framework.pagination import LimitOffsetPagination


class StoreKeepingStoreListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)

    permission_codename = "get.store"

    serializer_class = StoreKeepingStoreSerializer
    filterset_class = StoreFilter
    ordering_fields = '__all__'
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return Store.objects.exclude(id=PACKING_STORE_ID)


class StoreKeepingStoreApiView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)
    permission_basename = 'store'
    serializer_class = StoreKeepingStoreSerializer

    def perform_create(self, serializer):
        user = get_current_user()
        serializer.save(created_by=user, storekeeper=user)


class StoreKeepingStoreDetailView(APIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)
    permission_basename = 'store'

    def get_object(self, pk):
        try:
            return Store.objects.get(pk=pk)
        except Store.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        query = self.get_object(pk)
        serializers = StoreKeepingStoreSerializer(query)
        return Response(serializers.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        query = self.get_object(pk)
        serializer = StoreKeepingStoreSerializer(query, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        query = self.get_object(pk)
        query.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


