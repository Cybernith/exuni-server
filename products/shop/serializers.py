from rest_framework import serializers

from products.models import Product


class ShopProductsListSerializers(serializers.ModelSerializer):
    final_price = serializers.ReadOnlyField(source='final_price')
    effective_price = serializers.ReadOnlyField(source='effective_price')
    has_offer = serializers.ReadOnlyField(source='has_offer')
    offer_amount = serializers.ReadOnlyField(source='offer_amount')
    current_inventory = serializers.ReadOnlyField(source='current_inventory')

    image = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    brand = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id',
            'product_id',
            'name',
            'final_price',
            'effective_price',
            'has_offer',
            'offer_amount',
            'current_inventory',
            'image',
            'category',
            'brand',
        ]

    def get_image(self, obj):
        return obj.picture.url if obj.picture else None

    def get_brand(self, obj):
        return {'id': obj.brand.id, 'name': obj.brand.name} if obj.brand else None

    def get_category(self, obj):
        return {'id': obj.category.id, 'name': obj.category.name} if obj.category else None

