from django.db.models import Sum, F, DecimalField, Q
from rest_framework import serializers

from affiliate.models import AffiliateFactor, AffiliateFactorItem
from main.models import Business

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


class BusinessAffiliateReportSerializer(serializers.ModelSerializer):
    business_type_display = serializers.CharField(source='get_business_type_display', read_only=True)
    admin_name = serializers.CharField(source='admin.name', read_only=True)
    factors_count = serializers.SerializerMethodField(read_only=True)
    sale_price_sum = serializers.SerializerMethodField(read_only=True)
    sale_quantity_sum = serializers.SerializerMethodField(read_only=True)
    paid_price_sum = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Business
        fields = 'business_type_display', 'name', 'id', 'admin_name', 'domain_address', 'factors_count',\
                 'sale_quantity_sum', 'sale_price_sum', 'paid_price_sum'

    def get_factors_count(self, obj: Business):
        return AffiliateFactor.objects.filter(business=obj).count()

    def get_sale_price_sum(self, obj: Business):
        affiliate_factors = AffiliateFactor.objects.filter(business=obj).select_related('business')
        return AffiliateFactorItem.objects.filter(
                affiliate_factor__in=affiliate_factors).annotate(
                final_price=Sum(F('quantity') * F('price'), output_field=DecimalField()),
            ).aggregate(Sum('final_price'))['final_price__sum']

    def get_paid_price_sum(self, obj: Business):
        affiliate_factors = AffiliateFactor.objects.filter(
            Q(status=AffiliateFactor.PAID) & Q(business=obj)).select_related('business')
        return AffiliateFactorItem.objects.filter(
                affiliate_factor__in=affiliate_factors).annotate(
                final_price=Sum(F('quantity') * F('price'), output_field=DecimalField()),
            ).aggregate(Sum('final_price'))['final_price__sum']

    def get_sale_quantity_sum(self, obj: Business):
        affiliate_factors = AffiliateFactor.objects.filter(business=obj).select_related('business')
        return AffiliateFactorItem.objects.filter(
                affiliate_factor__in=affiliate_factors).aggregate(Sum('quantity'))['quantity__sum']

