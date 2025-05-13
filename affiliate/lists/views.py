from rest_framework import generics
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated

from affiliate.views import get_business_from_request
from helpers.auth import BasicObjectPermission

from affiliate.serializers import AffiliateFactorListSerializer, BusinessAffiliateReportSerializer
from affiliate.lists.filters import AffiliateFactorFilter, AffiliateCustomersFilter

from affiliate.models import AffiliateFactor
from main.lists.filters import BusinessFilter
from main.models import Business
from users.filters import UserNotificationFilter
from users.serializers import UserSimpleSerializer


class AffiliateFactorListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)

    permission_codename = "get.affiliate_factor"

    serializer_class = AffiliateFactorListSerializer
    filterset_class = AffiliateFactorFilter
    ordering_fields = '__all__'
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        business = get_business_from_request(self.request)
        return AffiliateFactor.objects.filter(business=business)


class AffiliateCustomersListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)

    permission_codename = "get.user"

    serializer_class = UserSimpleSerializer
    filterset_class = AffiliateCustomersFilter
    ordering_fields = '__all__'
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        business = get_business_from_request(self.request)
        return business.customers.all()


class BusinessAffiliateReportListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, BasicObjectPermission)

    permission_codename = "get.business"

    serializer_class = BusinessAffiliateReportSerializer
    filterset_class = BusinessFilter
    ordering_fields = '__all__'
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return Business.objects.all()
