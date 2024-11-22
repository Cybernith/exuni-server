from rest_framework import serializers

from affiliate.models import AffiliateFactor, AffiliateFactorItem

from products.serializers import ProductSimpleSerializer

from main.serializers import BusinessSerializer
from users.serializers import UserSimpleSerializer


class AffiliateFactorCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = AffiliateFactor
        fields = 'business', 'customer_name', 'phone', 'address', 'postal_code'


class AffiliateFactorItemsListSerializer(serializers.ModelSerializer):
    product = ProductSimpleSerializer(read_only=True)

    class Meta:
        model = AffiliateFactorItem
        fields = '__all__'


class AffiliateFactorListSerializer(serializers.ModelSerializer):
    items = AffiliateFactorItemsListSerializer(many=True, read_only=True)
    business = BusinessSerializer(read_only=True)
    customer = UserSimpleSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    factor_price_sum = serializers.ReadOnlyField()

    class Meta:
        model = AffiliateFactor
        fields = '__all__'
