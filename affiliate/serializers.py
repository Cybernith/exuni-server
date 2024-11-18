from rest_framework import serializers

from entrance.models import StoreReceiptItem
from helpers.functions import change_to_num
from helpers.serializers import SModelSerializer
from users.serializers import UserSimpleSerializer

from django.db.models import Sum, IntegerField, Q, Count, F

from affiliate.models import AffiliateFactor, AffiliateFactorItem


class AffiliateFactorCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = AffiliateFactor
        fields = 'business', 'customer_name', 'phone', 'address', 'postal_code'


class AffiliateFactorItemCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = AffiliateFactorItem
        read_only_fields = ('created_at', 'updated_at')
        fields = '__all__'
