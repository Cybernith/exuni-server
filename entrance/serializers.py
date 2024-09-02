from entrance.models import EntrancePackageItem, EntrancePackage
from helpers.serializers import SModelSerializer
from rest_framework import serializers

from main.serializers import SupplierSerializer, StoreSerializer
from users.serializers import UserSimpleSerializer


class EntrancePackageItemSerializer(SModelSerializer):
    class Meta:
        model = EntrancePackageItem
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

    def update(self, instance, validated_data):
        if instance.entrance_packages.is_verified:
            raise serializers.ValidationError("پکیج ورود غیر قابل ویرایش می باشند")
        return super(EntrancePackageItemSerializer, self).update(instance, validated_data)


class EntrancePackageItemListRetrieveSerializer(EntrancePackageItemSerializer):
    class Meta(EntrancePackageItemSerializer.Meta):
        pass


class EntrancePackageSerializer(SModelSerializer):
    class Meta:
        model = EntrancePackage
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

    def update(self, instance, validated_data):
        if instance.is_verified:
            raise serializers.ValidationError("پکیج ورود غیر قابل ویرایش می باشند")
        return super(EntrancePackageSerializer, self).update(instance, validated_data)


class EntrancePackageRetrieveSerializer(EntrancePackageSerializer):
    items = EntrancePackageItemListRetrieveSerializer(read_only=True, many=True)
    supplier = SupplierSerializer(read_only=True, many=True)
    store = StoreSerializer(read_only=True, many=True)
    created_by = UserSimpleSerializer(read_only=True)
    manager = UserSimpleSerializer(read_only=True)

    class Meta(EntrancePackageSerializer.Meta):
        fields = '__all__'


class EntrancePackageListSerializer(SModelSerializer):
    created_by = UserSimpleSerializer(many=False)

    class Meta:
        model = EntrancePackage
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

