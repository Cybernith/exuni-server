from rest_framework import serializers

from helpers.functions import get_current_user
from main.models import Store
from products.exuni_admin.serializers import AdminVariationSerializer
from products.models import Product
from store_handle.models import ProductHandleChange, ProductPackingInventoryHandle, ProductStoreInventory, \
    ProductStoreInventoryHandle


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
