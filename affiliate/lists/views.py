from rest_framework import generics
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated

from affiliate.views import get_business_from_request
from helpers.auth import BasicObjectPermission

from affiliate.serializers import AffiliateFactorListSerializer

from affiliate.lists.filters import AffiliateFactorFilter

from affiliate.models import AffiliateFactor


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


