from entrance.models import EntrancePackageItem, EntrancePackage, StoreReceiptItem, StoreReceipt
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
    items = EntrancePackageItemSerializer(read_only=True, many=True)

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


class StoreReceiptItemSerializer(SModelSerializer):
    class Meta:
        model = StoreReceiptItem
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

    def update(self, instance, validated_data):
        if instance.store_receipt.is_verified:
            raise serializers.ValidationError("ردیف رسید ورود انبار غیر قابل ویرایش می باشند")
        return super(StoreReceiptItemSerializer, self).update(instance, validated_data)


class StoreReceiptItemListRetrieveSerializer(StoreReceiptItemSerializer):
    class Meta(StoreReceiptItemSerializer.Meta):
        pass


class StoreReceiptSerializer(SModelSerializer):
    class Meta:
        model = StoreReceipt
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

    def update(self, instance, validated_data):
        if instance.is_verified:
            raise serializers.ValidationError("رسید ورود انبار غیر قابل ویرایش می باشند")
        return super(StoreReceiptSerializer, self).update(instance, validated_data)


class StoreReceiptRetrieveSerializer(StoreReceiptSerializer):
    items = StoreReceiptItemListRetrieveSerializer(read_only=True, many=True)
    entrance_packages = EntrancePackageSerializer(read_only=True, many=True)
    store = StoreSerializer(read_only=True, many=True)
    created_by = UserSimpleSerializer(read_only=True)
    storekeeper = UserSimpleSerializer(read_only=True)

    class Meta(StoreReceiptSerializer.Meta):
        fields = '__all__'


class StoreReceiptListSerializer(SModelSerializer):
    created_by = UserSimpleSerializer(many=False)

    class Meta:
        model = StoreReceipt
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class EntrancePackageFileUploadSerializer(SModelSerializer):
        entrance_file = serializers.FileField(required=False)

        class Meta:
            model = EntrancePackage
            fields = ('id', 'entrance_file')

