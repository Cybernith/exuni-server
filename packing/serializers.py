from rest_framework import serializers

from packing.models import OrderPackage, OrderPackageItem


class OrderPackageSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderPackage
        fields = '__all__'


class OrderPackageItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderPackageItem
        fields = '__all__'
