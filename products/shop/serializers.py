from rest_framework import serializers

from products.models import Product
from products.serializers import ProductGallerySerializer, AvailSerializer, ProductPropertySerializer
from shop.serializers import CommentRepliesSerializer


class ShopProductsListSerializers(serializers.ModelSerializer):
    final_price = serializers.ReadOnlyField(source='final_price')
    effective_price = serializers.ReadOnlyField(source='effective_price')
    has_offer = serializers.ReadOnlyField(source='has_offer')
    offer_amount = serializers.ReadOnlyField(source='offer_amount')
    current_inventory = serializers.ReadOnlyField(source='current_inventory')
    rate = serializers.ReadOnlyField(source='rate')
    offer_display = serializers.ReadOnlyField(source='offer_display')
    in_wish_list_count = serializers.ReadOnlyField(source='in_wish_list_count')

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
            'rate',
            'offer_display',
            'in_wish_list_count',
        ]

    def get_image(self, obj):
        return obj.picture.url if obj.picture else None

    def get_brand(self, obj):
        return {'id': obj.brand.id, 'name': obj.brand.name} if obj.brand else None

    def get_category(self, obj):
        return {'id': obj.category.id, 'name': obj.category.name} if obj.category else None


class ShopProductDetailSerializers(serializers.ModelSerializer):
    final_price = serializers.ReadOnlyField(source='final_price')
    rate = serializers.ReadOnlyField(source='rate')
    effective_price = serializers.ReadOnlyField(source='effective_price')
    has_offer = serializers.ReadOnlyField(source='has_offer')
    offer_amount = serializers.ReadOnlyField(source='offer_amount')
    current_inventory = serializers.ReadOnlyField(source='current_inventory')
    gallery = ProductGallerySerializer(read_only=True)
    avails = AvailSerializer(many=True, read_only=True)
    properties = ProductPropertySerializer(many=True, read_only=True)
    image = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    brand = serializers.SerializerMethodField()
    product_comments = CommentRepliesSerializer(many=True, read_only=True)
    offer_display = serializers.ReadOnlyField(source='offer_display')
    in_wish_list_count = serializers.ReadOnlyField(source='in_wish_list_count')
    comments_count = serializers.ReadOnlyField(source='comments_count')

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
            'gallery',
            'avails',
            'properties',
            'explanation',
            'summary_explanation',
            'how_to_use',
            'length',
            'width',
            'height',
            'postal_weight',
            'rate',
            'product_comments',
            'offer_display',
            'in_wish_list_count',
            'comments_count',
        ]

    def get_image(self, obj):
        return obj.picture.url if obj.picture else None

    def get_brand(self, obj):
        return {'id': obj.brand.id, 'name': obj.brand.name, 'logo': obj.brand.logo} if obj.brand else None

    def get_category(self, obj):
        return {'id': obj.category.id, 'name': obj.category.name} if obj.category else None

