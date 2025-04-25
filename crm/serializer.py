from django.shortcuts import get_object_or_404
from rest_framework import serializers

from crm.models import ShopProductViewLog
from products.models import Product


class ShopProductViewLogCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopProductViewLog
        field = ['ip_address', 'referer', 'device_type', 'user_agent']

    def create(self, validated_data):
        request = self.context['request']
        product = get_object_or_404(Product, pk=self.context['view'].kwargs['product_id'])
        return ShopProductViewLog.objects.create(
            product=product,
            user=request.user if request.user.is_authenticated else None,
            **validated_data
        )


class ShopProductViewLogSerializer(serializers.ModelSerializer):
    device_type = serializers.CharField(source='get_device_type_display', read_only=True)
    user_name = serializers.CharField(source='user.name', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = ShopProductViewLog
        fields = '__all__'
