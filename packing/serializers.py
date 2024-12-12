from rest_framework import serializers

from main.serializers import BusinessSerializer
from packing.models import OrderPackage, OrderPackageItem
from users.serializers import UserSimpleSerializer


class OrderPackageItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderPackageItem
        fields = '__all__'


class OrderPackageSerializer(serializers.ModelSerializer):
    items = OrderPackageItemSerializer(many=True, read_only=True)
    business = BusinessSerializer(read_only=True)
    customer = UserSimpleSerializer(read_only=True)
    products_quantity = serializers.ReadOnlyField()

    class Meta:
        model = OrderPackage
        fields = '__all__'
