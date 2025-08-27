import datetime

from django.db.models import Sum, F, Value, FloatField
from django.db.models.functions import Coalesce

from entrance.models import EntrancePackageItem, EntrancePackage, StoreReceiptItem, StoreReceipt, \
    ChinaEntrancePackageItem, ChinaEntrancePackage, ChinaEntrancePackageDeliveryItem, ChinaEntrancePackageDelivery
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
    profit_type_name = serializers.CharField(source='get_profit_type_display', read_only=True)
    profit = serializers.SerializerMethodField()
    toman = serializers.SerializerMethodField()
    total_final = serializers.SerializerMethodField()

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

    def get_total_final(self, obj):
        if obj.total_quantity:
            return obj.total_quantity * obj.final_amount
        qpb = obj.quantity_per_box if obj.quantity_per_box else 1
        bq = obj.box_quantity if obj.box_quantity else 1
        return qpb * bq * obj.final_amount

    def get_toman(self, obj):
        currency_rate = 1
        if obj.packing.currency:
            currency_rate = float(obj.packing.currency.exchange_rate_to_toman)

        if not obj.profit_margin:
            obj.profit_margin = 0

        return obj.price * currency_rate

    def get_profit(self, obj):
        currency_rate = 1
        if obj.packing.currency:
            currency_rate = float(obj.packing.currency.exchange_rate_to_toman)

        if not obj.profit_margin:
            obj.profit_margin = 0

        base_price_with_rate = obj.price * currency_rate
        if obj.profit_type == obj.PERCENT:
            profit_amount = base_price_with_rate / 100 * float(obj.profit_margin)
        else:
            profit_amount = float(obj.profit_margin)
        return profit_amount


class ChinaEntrancePackageSerializer(serializers.ModelSerializer):
    items = ChinaEntrancePackageItemSerializer(many=True, read_only=True)
    items_count = serializers.SerializerMethodField()
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    xlsx_file_name = serializers.CharField(source='xlsx_file.name', read_only=True)
    currency_name = serializers.CharField(source='currency.name', read_only=True)
    currency_rate = serializers.CharField(source='currency.exchange_rate_to_toman', read_only=True)
    base_amount = serializers.SerializerMethodField()
    final_amount = serializers.SerializerMethodField()

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

    def get_final_amount(self, obj):
        return obj.items.aggregate(
            total=Sum(
                Coalesce(F('quantity_per_box'), Value(1), output_field=FloatField()) *
                Coalesce(F('box_quantity'), Value(1), output_field=FloatField()) *
                Coalesce(F('final_amount'), Value(0), output_field=FloatField())
            )
        )['total'] or 0


class PendingChinaEntrancePackageItemSerializer(serializers.ModelSerializer):
    pic = serializers.SerializerMethodField()
    delivered_boxes = serializers.ReadOnlyField()
    pending_boxes = serializers.ReadOnlyField()

    total_items = serializers.ReadOnlyField()
    delivered_items = serializers.ReadOnlyField()
    pending_items = serializers.ReadOnlyField()

    class Meta:
        model = ChinaEntrancePackageItem
        fields = [
            "id", "group_id", "name", "price", "pic",
            "box_quantity", "quantity_per_box",
            "delivered_boxes", "pending_boxes", "box_stacking",
            "total_items", "delivered_items", "pending_items",
        ]

    def get_pic(self, obj):
        return obj.image.url if obj.image else None


class PendingChinaEntrancePackageSerializer(serializers.ModelSerializer):
    total_boxes = serializers.IntegerField(read_only=True)
    delivered_boxes = serializers.IntegerField(read_only=True)
    pending_boxes = serializers.IntegerField(read_only=True)

    total_items = serializers.IntegerField(read_only=True)
    delivered_items = serializers.IntegerField(read_only=True)
    pending_items = serializers.IntegerField(read_only=True)

    pending_rows = serializers.SerializerMethodField()
    items = PendingChinaEntrancePackageItemSerializer(many=True, read_only=True)

    class Meta:
        model = ChinaEntrancePackage
        fields = [
            "id", "title", "factor_number", "registration_date",
            "is_received", "is_verified", "explanation",
            "total_boxes", "delivered_boxes", "pending_boxes",
            "total_items", "delivered_items", "pending_items",
            "items", 'pending_rows'
        ]

    def get_pending_rows(self, obj):
        pending_items_qs = obj.items.all()
        pending_items_qs = [item for item in pending_items_qs if item.pending_items > 0]
        return PendingChinaEntrancePackageItemSerializer(pending_items_qs, many=True, context=self.context).data


class ChinaEntrancePackageDeliveryItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChinaEntrancePackageDeliveryItem
        fields = ["package_item", "boxes_delivered", "quantity_per_box"]


class ChinaEntrancePackageDeliveryCreateSerializer(serializers.ModelSerializer):
    items = ChinaEntrancePackageDeliveryItemCreateSerializer(many=True)

    class Meta:
        model = ChinaEntrancePackageDelivery
        fields = ["package", "delivery_date", "driver_name", "driver_mobile_number",
                  "document_number", "total_boxes", "items", 'id']
        read_only_fields = ('delivery_date', )

    def create(self, validated_data):
        items_data = validated_data.pop("items")
        delivery = ChinaEntrancePackageDelivery.objects.create(delivery_date=datetime.date.today(), **validated_data)
        for item_data in items_data:
            ChinaEntrancePackageDeliveryItem.objects.create(delivery=delivery, **item_data)
        return delivery


class ChinaEntrancePackageDeliveryItemUpdateSerializer(serializers.ModelSerializer):
    crashed_quantity = serializers.IntegerField(write_only=True, required=False)
    postal_weight = serializers.FloatField(write_only=True, required=True)
    length = serializers.FloatField(write_only=True, required=True)
    width = serializers.FloatField(write_only=True, required=True)
    height = serializers.FloatField(write_only=True, required=True)
    expired_date = serializers.CharField(write_only=True, required=True)
    sku = serializers.CharField(write_only=True, required=True)
    aisle = serializers.CharField(write_only=True, required=True)
    shelf_number = serializers.CharField(write_only=True, required=True)
    min_inventory = serializers.FloatField(write_only=True, required=True)
    to_store = serializers.IntegerField(write_only=True, required=True)

    package_item = serializers.PrimaryKeyRelatedField(read_only=True)
    boxes_delivered = serializers.IntegerField(read_only=True)
    quantity_per_box = serializers.IntegerField(read_only=True)
    pic = serializers.SerializerMethodField()
    group_id = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()

    class Meta:
        model = ChinaEntrancePackageDeliveryItem
        fields = [
            "id",
            # write-only
            "sku",
            "crashed_quantity",
            "postal_weight",
            "length",
            "width",
            "height",
            "expired_date",
            "aisle",
            "shelf_number",
            "min_inventory",
            "to_store",
            # read-only
            "package_item",
            "boxes_delivered",
            "quantity_per_box",
            "pic",
            "group_id",
            "name",
        ]

    def get_pic(self, obj):
        return obj.package_item.image.url if obj.package_item.image else None

    def get_name(self, obj):
        return obj.package_item.name or None

    def get_group_id(self, obj):
        return obj.package_item.group_id or None


class ChinaEntrancePackageDeliveryUpdateItemsSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()

    class Meta:
        model = ChinaEntrancePackageDelivery
        fields = "__all__"

    def get_items(self, obj):
        data = obj.items.filter(inserted=False)
        return ChinaEntrancePackageDeliveryItemUpdateSerializer(data, many=True, context=self.context).data


class InsertedPackageDeliveryItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChinaEntrancePackageDeliveryItem
        fields = "__all__"
