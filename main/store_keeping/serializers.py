from rest_framework import serializers
from main.models import Store


class StoreKeepingStoreSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.name', read_only=True)
    storekeeper_name = serializers.CharField(source='storekeeper.name', read_only=True)

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = Store
        fields = ('id', 'name', 'address', 'storekeeper_name', 'created_by_name')
