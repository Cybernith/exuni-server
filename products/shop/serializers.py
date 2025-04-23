from django.db.models import Q
from rest_framework import serializers

from products.models import Product
from products.serializers import ProductGallerySerializer, AvailSerializer, ProductPropertySerializer
from shop.models import Comment, Rate
from shop.serializers import CommentRepliesSerializer, CommentSerializer


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
    avails = AvailSerializer(many=True, read_only=True)
    properties = ProductPropertySerializer(many=True, read_only=True)

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
            'avails',
            'properties',
        ]

    def get_image(self, obj):
        return obj.picture.url if obj.picture else None

    def get_brand(self, obj):
        return {'id': obj.brand.id, 'name': obj.brand.name} if obj.brand else None

    def get_category(self, obj):
        return {'id': obj.category.id, 'name': obj.category.name} if obj.category else None


class ShopSimilarProductsListSerializers(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'image',
        ]

    def get_image(self, obj):
        return obj.picture.url if obj.picture else None


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
    similar_products = serializers.SerializerMethodField()
    similar_brand_products = serializers.SerializerMethodField()
    offer_display = serializers.ReadOnlyField(source='offer_display')
    in_wish_list_count = serializers.ReadOnlyField(source='in_wish_list_count')
    #comments = serializers.SerializerMethodField()
    user_rate = serializers.SerializerMethodField()
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
            'user_rate',
            'offer_display',
            'in_wish_list_count',
            #'comments',
            'comments_count',
            'similar_products',
            'similar_brand_products',
        ]

    def get_image(self, obj):
        return obj.picture.url if obj.picture else None

    def get_user_rate(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            rate = Rate.objects.filter(customer=user, product=obj).first()
            return rate.level if rate else None
        return None

    def get_brand(self, obj):
        return {'id': obj.brand.id, 'name': obj.brand.name, 'logo': obj.brand.logo} if obj.brand else None

    def get_category(self, obj):
        return {'id': obj.category.id, 'name': obj.category.name} if obj.category else None

    def get_similar_products(self, obj):
        similar_products = Product.objects.filter(
            Q(category=obj.category) |
            Q(avails__in=obj.avails) |
            Q(properties__in=obj.properties)
        ).only('id', 'name', 'picture').exclude(id=obj.id)[:10]

        return ShopSimilarProductsListSerializers(similar_products, many=True).data

    def get_similar_brand_products(self, obj):
        similar_products = Product.objects.filter(brand=obj.brand).only('id', 'name', 'picture').exclude(id=obj.id)[:10]

        return ShopSimilarProductsListSerializers(similar_products, many=True).data

    #def get_comments(self, obj):
    #    comments = obj.product_comments.filter()[:4]
    #    return CommentSerializer(comments, many=True).data


class ShopCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'product', 'shop_order', 'reply', 'text', 'file', 'date_time']
        read_only_fields = ['id', 'date_time']

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['customer'] = request.user
        return super().create(validated_data)


class ShopProductRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rate
        fields = ['id', 'product', 'level']

    def create(self, validated_data):
        user = self.context['request'].user
        product = self.context['product']
        level = self.context['level']

        rate_object, created = Rate.objects.update_or_create(
            customer=user,
            product=product,
            level=level,
        )
        return rate_object

