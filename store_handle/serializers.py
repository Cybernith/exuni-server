from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum
from rest_framework import serializers

from helpers.functions import get_current_user
from main.models import Store
from products.exuni_admin.serializers import AdminVariationSerializer
from products.models import Product
from server.store_configs import PACKING_STORE_ID
from store_handle.models import ProductHandleChange, ProductPackingInventoryHandle, ProductStoreInventory, \
    ProductStoreInventoryHandle, InventoryTransfer


class ProductHandleChangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductHandleChange
        fields = '__all__'
        read_only_fields = ('product', 'timestamp', 'changed_by', 'is_applied',)


class ProductPackingInventoryHandleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductPackingInventoryHandle
        fields = '__all__'
        read_only_fields = ('product', 'timestamp', 'changed_by', 'is_applied',)


class ProductStoreInventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductStoreInventory
        fields = '__all__'
        read_only_fields = ('product', 'store', 'last_updated')


class StoreHandlingProductsListSerializers(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    packing_inventory = serializers.SerializerMethodField()
    minimum_packing_inventory = serializers.SerializerMethodField()
    is_variable = serializers.SerializerMethodField()
    variations = AdminVariationSerializer(many=True, read_only=True)
    variation_of = AdminVariationSerializer(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'image',
            'sixteen_digit_code',
            'variations',
            'minimum_packing_inventory',
            'packing_inventory',
            'aisle',
            'is_variable',
            'variation_of',
            'shelf_number',
            'price',

        ]

    def get_is_variable(self, obj):
        return obj.product_type == Product.VARIABLE

    def get_image(self, obj):
        return obj.picture.url if obj.picture else None

    def get_packing_inventory(self, obj):
        try:
            return ProductStoreInventory.objects.get(
                product=obj, store=Store.objects.get(code=Store.PACKING)
            ).inventory
        except:
            return None

    def get_minimum_packing_inventory(self, obj):
        try:
            return ProductStoreInventory.objects.get(
                product=obj, store=Store.objects.get(code=Store.PACKING)
            ).minimum_inventory
        except:
            return None


class ProductStoreInventoryHandleSerializer(serializers.ModelSerializer):
    store_inventory = serializers.IntegerField(write_only=True)

    class Meta:
        model = ProductStoreInventoryHandle
        fields = ['store', 'product', 'store_inventory']

    def create(self, validated_data):
        store_inventory = validated_data.pop('store_inventory')
        user = get_current_user()

        handle = ProductStoreInventoryHandle.objects.create(
            store=validated_data['store'],
            product=validated_data['product'],
            inventory=store_inventory,
            changed_by=user
        )
        validated_data['product'].update(store_handle_done=True)
        return handle


class StoreInventoryHandleDoneSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductStoreInventoryHandle
        fields = '__all__'


class HandleDoneProductsListSerializers(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    packing_inventory = serializers.SerializerMethodField()
    minimum_packing_inventory = serializers.SerializerMethodField()
    is_variable = serializers.SerializerMethodField()
    variations = AdminVariationSerializer(many=True, read_only=True)
    variation_of = AdminVariationSerializer(read_only=True)
    store_handle = StoreInventoryHandleDoneSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'image',
            'sixteen_digit_code',
            'variations',
            'minimum_packing_inventory',
            'packing_inventory',
            'aisle',
            'is_variable',
            'variation_of',
            'shelf_number',
            'price',
            'store_handle',

        ]

    def get_is_variable(self, obj):
        return obj.product_type == Product.VARIABLE

    def get_image(self, obj):
        return obj.picture.url if obj.picture else None

    def get_packing_inventory(self, obj):
        try:
            return ProductStoreInventory.objects.get(
                product=obj, store=Store.objects.get(code=Store.PACKING)
            ).inventory
        except:
            return None

    def get_minimum_packing_inventory(self, obj):
        try:
            return ProductStoreInventory.objects.get(
                product=obj, store=Store.objects.get(code=Store.PACKING)
            ).minimum_inventory
        except:
            return None


class StoreInventoryUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductStoreInventoryHandle
        fields = ['store', 'inventory']

    def update(self, instance, validated_data):
        instance.inventory = validated_data.get('inventory', instance.inventory)
        instance.store = validated_data.get('store', instance.store)
        instance.changed_by = get_current_user()
        instance.save()
        return instance


class InventoryTransferSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(write_only=True)
    from_store_id = serializers.IntegerField(write_only=True)
    to_store_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = InventoryTransfer
        fields = ["id", "product_id", "from_store_id", "to_store_id", "quantity"]

    def validate(self, attrs):
        product_id = attrs["product_id"]
        from_store_id = attrs["from_store_id"]
        to_store_id = attrs["to_store_id"]
        quantity = attrs["quantity"]

        if from_store_id == to_store_id:
            raise serializers.ValidationError("مبدا و مقصد نمی‌توانند یکسان باشند.")
        if quantity <= 0:
            raise serializers.ValidationError("تعداد باید بیشتر از صفر باشد.")

        try:
            from_inventory = ProductStoreInventory.objects.get(product_id=product_id, store_id=from_store_id)
        except ProductStoreInventory.DoesNotExist:
            raise serializers.ValidationError("محصول در انبار مبدا یافت نشد.")

        try:
            to_inventory, _ = ProductStoreInventory.objects.get_or_create(
                product_id=product_id,
                store_id=to_store_id,
                defaults={"inventory": 0}
            )
        except ProductStoreInventory.DoesNotExist:
            raise serializers.ValidationError("محصول در انبار مقصد یافت نشد.")

        if from_inventory.inventory < quantity:
            raise serializers.ValidationError(f"موجودی کافی در {from_inventory.store.name} وجود ندارد.")

        attrs["from_inventory"] = from_inventory
        attrs["to_inventory"] = to_inventory

        return attrs

    def create(self, validated_data):
        from_inventory = validated_data.pop("from_inventory")
        to_inventory = validated_data.pop("to_inventory")
        quantity = validated_data["quantity"]
        user = self.context["request"].user if self.context.get("request") else None

        from_inventory.reduce_inventory_in_store(quantity, user=user)
        to_inventory.increase_inventory_in_store(quantity, user=user)

        transfer = InventoryTransfer.objects.create(
            from_store=from_inventory,
            to_store=to_inventory,
            quantity=quantity
        )
        return transfer


class ProductStoreInventoryListSerializers(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    is_variable = serializers.SerializerMethodField()
    variation_of = serializers.SerializerMethodField()
    sixteen_digit_code = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    product_type = serializers.SerializerMethodField()
    product_id = serializers.SerializerMethodField()
    is_minimum = serializers.SerializerMethodField()
    in_store = serializers.SerializerMethodField()
    total_inventory = serializers.SerializerMethodField()
    transfer_quantity = serializers.SerializerMethodField()

    class Meta:
        model = ProductStoreInventory
        fields = [
            'is_minimum',
            'id',
            'product_id',
            'store',
            'store',
            'name',
            'product_type',
            'product',
            'product_id',
            'image',
            'sixteen_digit_code',
            'inventory',
            'is_variable',
            'product_type',
            'variation_of',
            'minimum_inventory',
            'in_store',
            'total_inventory',
            'transfer_quantity',

        ]

    def get_is_minimum(self, obj):
        total_inventory = obj.product.store_inventory.exclude(
            store_id=PACKING_STORE_ID).aggregate(total=Sum('inventory'))['total'] or 0
        if total_inventory < 1:
            return False
        if not obj.minimum_inventory or obj.minimum_inventory == 0:
            if obj.inventory < 1:
                return True
        else:
            return obj.minimum_inventory > obj.inventory


    def get_transfer_quantity(self, obj):
        total_inventory = obj.product.store_inventory.exclude(
            store_id=PACKING_STORE_ID).aggregate(total=Sum('inventory'))['total'] or 0
        if total_inventory:
            minimum = obj.minimum_inventory or 0
            inventory = obj.inventory
            transfer_quantity = minimum - inventory
            return min(transfer_quantity, total_inventory)
        else:
            return obj.minimum_inventory > obj.inventory

    def get_total_inventory(self, obj):
        return obj.product.store_inventory.exclude(
            store_id=PACKING_STORE_ID).aggregate(total=Sum('inventory'))['total'] or 0

    def get_is_variable(self, obj):
        return obj.product.product_type == Product.VARIABLE

    def get_in_store(self, obj):
        store = obj.product.store_inventory.exclude(store_id=PACKING_STORE_ID).first()
        return {
            'id': store.first().store.id,
            'name': store.first().store.name,
        } if store.exists() else None

    def get_product_id(self, obj):
        return obj.product.id

    def get_product_type(self, obj):
        return obj.product.product_type

    def get_name(self, obj):
        return obj.product.name

    def get_image(self, obj):
        return obj.product.picture.url if obj.product.picture else None

    def get_sixteen_digit_code(self, obj):
        return obj.product.sixteen_digit_code if obj.product.sixteen_digit_code else None

    def get_variation_of(self, obj):
        if hasattr(obj, "product") and obj.product and obj.product.variation_of:
            return AdminVariationSerializer(obj.product.variation_of).data
        return None
