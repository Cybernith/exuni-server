from django.http import Http404
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView

from rest_framework.response import Response
from rest_framework import status

from cms.models import HeaderElement, PopUpElement, BannerContent, BannerContentItem, ShopHomePageStory
from cms.serializers import HeaderElementSerializer, PopUpElementSerializer, BannerContentSerializer, \
    BannerContentItemSerializer, ShopHomePageStorySerializer
from cms.trottles import CMSUserRateThrottle, CMSAnonRateThrottle
from helpers.auth import BasicObjectPermission


class HeaderElementApiView(APIView):
    throttle_classes = [CMSUserRateThrottle, CMSAnonRateThrottle]

    def get(self, request):
        query = HeaderElement.objects.current_by_datetime()
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


class HeaderElementDetailView(APIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)
    permission_basename = 'header_element'

    def get_object(self, pk):
        try:
            return HeaderElement.objects.get(pk=pk)
        except HeaderElement.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        query = self.get_object(pk)
        serializers = HeaderElementSerializer(query)
        return Response(serializers.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        query = self.get_object(pk)
        serializer = HeaderElementSerializer(query, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        query = self.get_object(pk)
        query.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PopUpElementApiView(APIView):
    throttle_classes = [CMSUserRateThrottle, CMSAnonRateThrottle]

    def get(self, request):
        query = PopUpElement.objects.current_by_datetime()
        serializers = PopUpElementSerializer(query, many=True, context={'request': request})
        return Response(serializers.data, status=status.HTTP_200_OK)


class AllPopUpElementApiView(APIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)
    permission_basename = 'pop_up_element'

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


class PopUpElementDetailView(APIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)
    permission_basename = 'pop_up_element'

    def get_object(self, pk):
        try:
            return PopUpElement.objects.get(pk=pk)
        except PopUpElement.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        query = self.get_object(pk)
        serializers = PopUpElementSerializer(query)
        return Response(serializers.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        query = self.get_object(pk)
        serializer = PopUpElementSerializer(query, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        query = self.get_object(pk)
        query.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BannerContentApiView(APIView):
    throttle_classes = [CMSUserRateThrottle, CMSAnonRateThrottle]

    def get(self, request):
        order_one_query = BannerContent.objects.current_by_datetime().filter(order=BannerContent.ONE).first()
        order_two_query = BannerContent.objects.current_by_datetime().filter(order=BannerContent.TWO).first()
        order_three_query = BannerContent.objects.current_by_datetime().filter(order=BannerContent.THREE).first()
        order_four_query = BannerContent.objects.current_by_datetime().filter(order=BannerContent.FOUR).first()
        order_five_query = BannerContent.objects.current_by_datetime().filter(order=BannerContent.FIVE).first()
        query = {
            1: BannerContentSerializer(order_one_query, many=True),
            2: BannerContentSerializer(order_two_query, many=True),
            3: BannerContentSerializer(order_three_query, many=True),
            4: BannerContentSerializer(order_four_query, many=True),
            5: BannerContentSerializer(order_five_query, many=True),

        }
        return Response(query, status=status.HTTP_200_OK)


class AllBannerContentApiView(APIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)
    permission_basename = 'banner_content'

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


class BannerContentDetailView(APIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)
    permission_basename = 'banner_content'

    def get_object(self, pk):
        try:
            return BannerContent.objects.get(pk=pk)
        except BannerContent.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        query = self.get_object(pk)
        serializers = BannerContentSerializer(query)
        return Response(serializers.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        query = self.get_object(pk)
        serializer = BannerContentSerializer(query, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        query = self.get_object(pk)
        query.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BannerContentItemApiView(APIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)
    permission_basename = 'banner_content_item'

    def post(self, request):
        data = request.data
        serializer = BannerContentItemSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BannerContentItemDetailView(APIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)
    permission_basename = 'banner_content_item'

    def get_object(self, pk):
        try:
            return BannerContentItem.objects.get(pk=pk)
        except BannerContentItem.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        query = self.get_object(pk)
        serializers = BannerContentItemSerializer(query)
        return Response(serializers.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        query = self.get_object(pk)
        serializer = BannerContentItemSerializer(query, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        query = self.get_object(pk)
        query.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShopHomePageStoryApiView(APIView):
    throttle_classes = [CMSUserRateThrottle, CMSAnonRateThrottle]

    def get(self, request):
        query = ShopHomePageStory.objects.current_by_datetime()
        serializers = ShopHomePageStorySerializer(query, many=True, context={'request': request})
        return Response(serializers.data, status=status.HTTP_200_OK)


class AllShopHomePageStoryApiView(APIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)
    permission_basename = 'shop_home_page_story'

    def get(self, request):
        query = ShopHomePageStory.objects.all()
        serializers = ShopHomePageStorySerializer(query, many=True, context={'request': request})
        return Response(serializers.data, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.data
        serializer = ShopHomePageStorySerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ShopHomePageStoryDetailView(APIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)
    permission_basename = 'shop_home_page_story'

    def get_object(self, pk):
        try:
            return ShopHomePageStory.objects.get(pk=pk)
        except ShopHomePageStory.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        query = self.get_object(pk)
        serializers = ShopHomePageStorySerializer(query)
        return Response(serializers.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        query = self.get_object(pk)
        serializer = ShopHomePageStorySerializer(query, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        query = self.get_object(pk)
        query.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

