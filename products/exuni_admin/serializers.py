from rest_framework import serializers

from products.models import Product


class AdminProductSerializer(serializers.ModelSerializer):

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = Product
        fields = '__all__'

