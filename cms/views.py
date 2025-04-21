import datetime

from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from rest_framework.response import Response
from rest_framework import status

from cms.models import HeaderElement, PopUpElement, BannerContent
from cms.serializers import HeaderElementSerializer, PopUpElementSerializer, BannerContentSerializer
from helpers.auth import BasicObjectPermission


class HeaderElementApiView(APIView):

    def get(self, request):
        now = datetime.datetime.now()
        query = HeaderElement.objects.filter(Q(to_date_time__lte=now) & Q(from_date_time__gte=now))
        serializers = HeaderElementSerializer(query, many=True, context={'request': request})
        return Response(serializers.data, status=status.HTTP_200_OK)


class AllHeaderElementApiView(APIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)
    permission_basename = 'header_element'

    def get(self, request):
        query = HeaderElement.objects.all()
        serializers = HeaderElementSerializer(query, many=True, context={'request': request})
        return Response(serializers.data, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.data
        serializer = HeaderElementSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PopUpElementApiView(APIView):

    def get(self, request):
        now = datetime.datetime.now()
        query = PopUpElement.objects.filter(Q(to_date_time__lte=now) & Q(from_date_time__gte=now))
        serializers = PopUpElementSerializer(query, many=True, context={'request': request})
        return Response(serializers.data, status=status.HTTP_200_OK)


class AllPopUpElementApiView(APIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)
    permission_basename = 'header_element'

    def get(self, request):
        query = PopUpElement.objects.all()
        serializers = PopUpElementSerializer(query, many=True, context={'request': request})
        return Response(serializers.data, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.data
        serializer = PopUpElementSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BannerContentApiView(APIView):

    def get(self, request):
        now = datetime.datetime.now()
        query = BannerContent.objects.filter(Q(to_date_time__lte=now) & Q(from_date_time__gte=now))
        serializers = BannerContentSerializer(query, many=True, context={'request': request})
        return Response(serializers.data, status=status.HTTP_200_OK)


class AllBannerContentApiView(APIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)
    permission_basename = 'header_element'

    def get(self, request):
        query = BannerContent.objects.all()
        serializers = BannerContentSerializer(query, many=True, context={'request': request})
        return Response(serializers.data, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.data
        serializer = BannerContentSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

