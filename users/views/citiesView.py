from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from helpers.auth import BasicCRUDPermission
from users.models import City
from users.serializers import CitySerializer


class CityListCreateView(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated, BasicCRUDPermission)
    permission_basename = 'city'
    queryset = City.objects.all()
    serializer_class = CitySerializer


class CityDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated, BasicCRUDPermission)
    permission_basename = 'city'
    queryset = City.objects.all()
    serializer_class = CitySerializer
