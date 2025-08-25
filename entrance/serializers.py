from django.db.models import Sum, F, Value, FloatField
from django.db.models.functions import Coalesce

from entrance.models import EntrancePackageItem, EntrancePackage, StoreReceiptItem, StoreReceipt, \
    ChinaEntrancePackageItem, ChinaEntrancePackage
from helpers.serializers import SModelSerializer
from rest_framework import serializers

from main.serializers import SupplierSerializer, StoreSerializer
from users.serializers import UserSimpleSerializer


class EntrancePackageItemSerializer(SModelSerializer):
    net_purchase_price = serializers.ReadOnlyField()
    in_case_of_sale = serializers.ReadOnlyField()
    final_price_after_discount = serializers.ReadOnlyField()

    class Meta:
        model = EntrancePackageItem
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

    def update(self, instance, validated_data):
        if instance.entrance_packages.is_verified:
            raise serializers.ValidationError("پکیج ورود غیر قابل ویرایش می باشند")
        return super(EntrancePackageItemSerializer, self).update(instance, validated_data)


class EntrancePackageItemListRetrieveSerializer(EntrancePackageItemSerializer):
    net_purchase_price = serializers.ReadOnlyField()
    in_case_of_sale = serializers.ReadOnlyField()
    final_price_after_discount = serializers.ReadOnlyField()

    class Meta(EntrancePackageItemSerializer.Meta):
        pass


class EntrancePackageSerializer(SModelSerializer):
    remain_item = serializers.JSONField(source='remain_items', read_only=True)
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
    remain_item = serializers.JSONField(source='remain_items', read_only=True)
    items = EntrancePackageItemListRetrieveSerializer(read_only=True, many=True)
    supplier = SupplierSerializer(read_only=True, many=True)
    store = StoreSerializer(read_only=True, many=True)
    created_by = UserSimpleSerializer(read_only=True)
    manager = UserSimpleSerializer(read_only=True)

    class Meta(EntrancePackageSerializer.Meta):
        fields = '__all__'


class EntrancePackageListSerializer(SModelSerializer):
    remain_item = serializers.JSONField(source='remain_items', read_only=True)
    created_by = UserSimpleSerializer(many=False)
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    store_name = serializers.CharField(source='store.name', read_only=True)
    items = EntrancePackageItemListRetrieveSerializer(read_only=True, many=True)

    class Meta:
        model = EntrancePackage
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class StoreReceiptSimpleSerializer(SModelSerializer):
    store_name = serializers.CharField(source='store.name', read_only=True)
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)

    class Meta:
        model = StoreReceipt
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class StoreReceiptItemSerializer(SModelSerializer):
    store_receipt = StoreReceiptSimpleSerializer(read_only=True)

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
    items = StoreReceiptItemListRetrieveSerializer(read_only=True, many=True)
    store_name = serializers.CharField(source='store.name', read_only=True)

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
    items = StoreReceiptItemListRetrieveSerializer(read_only=True, many=True)

    class Meta:
        model = StoreReceipt
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class EntrancePackageFileUploadSerializer(SModelSerializer):
        entrance_file = serializers.FileField(required=False)

        class Meta:
            model = EntrancePackage
            fields = ('id', 'entrance_file')


class ChinaEntrancePackageItemSerializer(serializers.ModelSerializer):
    pic = serializers.SerializerMethodField()
    total = serializers.SerializerMethodField()
    base_amount_sum = serializers.ReadOnlyField()

    class Meta:
        model = ChinaEntrancePackageItem
        fields = "__all__"

    def get_pic(self, obj):
        return obj.image.url if obj.image else None

    def get_total(self, obj):
        if obj.total_quantity:
            return obj.total_quantity
        qpb = obj.quantity_per_box if obj.quantity_per_box else 1
        bq = obj.box_quantity if obj.box_quantity else 1
        return qpb * bq


class ChinaEntrancePackageSerializer(serializers.ModelSerializer):
    items = ChinaEntrancePackageItemSerializer(many=True, read_only=True)
    items_count = serializers.SerializerMethodField()
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    xlsx_file_name = serializers.CharField(source='xlsx_file.name', read_only=True)
    currency_name = serializers.CharField(source='currency.name', read_only=True)
    base_amount = serializers.SerializerMethodField()

    class Meta:
        model = ChinaEntrancePackage
        fields = "__all__"

    def get_items_count(self, obj):
        return obj.items.count()

    def get_base_amount(self, obj):
        return obj.items.aggregate(
            total=Sum(
                Coalesce(F('quantity_per_box'), Value(1), output_field=FloatField()) *
                Coalesce(F('box_quantity'), Value(1), output_field=FloatField()) *
                Coalesce(F('price'), Value(0), output_field=FloatField())
            )
        )['total'] or 0

