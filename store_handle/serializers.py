from rest_framework import serializers

from main.models import Store
from products.exuni_admin.serializers import AdminVariationSerializer
from products.models import Product
from store_handle.models import ProductHandleChange, ProductPackingInventoryHandle, ProductStoreInventory


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


