from rest_framework import serializers

from main.models import Business, Store, Currency, Supplier


class BusinessSerializer(serializers.ModelSerializer):
    business_type_display = serializers.CharField(source='get_business_type_display', read_only=True)

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = Business
        fields = '__all__'


class StoreSerializer(serializers.ModelSerializer):

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = Store
        fields = '__all__'


class CurrencySerializer(serializers.ModelSerializer):

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = Currency
        fields = '__all__'


class SupplierSerializer(serializers.ModelSerializer):

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = Supplier
        fields = '__all__'
