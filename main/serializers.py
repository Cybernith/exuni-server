from rest_framework import serializers

from main.models import Business, Store, Currency, Supplier
from users.serializers import UserSimpleSerializer


class BusinessSerializer(serializers.ModelSerializer):
    created_by = UserSimpleSerializer(read_only=True)
    business_type_display = serializers.CharField(source='get_business_type_display', read_only=True)

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = Business
        fields = '__all__'


class StoreSerializer(serializers.ModelSerializer):
    created_by = UserSimpleSerializer(read_only=True)
    storekeeper_name = serializers.CharField(source='storekeeper.name', read_only=True)

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = Store
        fields = '__all__'


class CurrencySerializer(serializers.ModelSerializer):
    created_by = UserSimpleSerializer(read_only=True)

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = Currency
        fields = '__all__'


class SupplierSerializer(serializers.ModelSerializer):
    created_by = UserSimpleSerializer(read_only=True)
    admin_name = serializers.CharField(source='admin.name', read_only=True)

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = Supplier
        fields = '__all__'
