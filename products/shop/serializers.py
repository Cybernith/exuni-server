from django.db.models import Q
from rest_framework import serializers

from helpers.functions import get_current_user
from products.models import Product, ProductGallery, Category
from products.serializers import ProductGallerySerializer, AvailSerializer, ProductPropertySerializer, \
    BrandShopListSerializer
from shop.models import Comment, Rate, WishList, Comparison
from shop.serializers import CommentRepliesSerializer, CommentSerializer


class ShopProductsListSerializers(serializers.ModelSerializer):
    final_price = serializers.ReadOnlyField()
    effective_price = serializers.ReadOnlyField()
    has_offer = serializers.ReadOnlyField()
    offer_amount = serializers.ReadOnlyField()
    calculate_current_inventory = serializers.ReadOnlyField()
    rate = serializers.ReadOnlyField()
    offer_display = serializers.ReadOnlyField()
    in_wish_list_count = serializers.ReadOnlyField()

    image = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    brand = serializers.SerializerMethodField()
    avails = AvailSerializer(many=True, read_only=True)
    properties = ProductPropertySerializer(many=True, read_only=True)
    view_count = serializers.IntegerField(read_only=True)

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
            'calculate_current_inventory',
            'image',
            'category',
            'brand',
            'rate',
            'offer_display',
            'in_wish_list_count',
            'avails',
            'properties',
            'view_count',
        ]

    def get_image(self, obj):
        return obj.picture.url if obj.picture else None

    def get_brand(self, obj):
        return {'id': obj.brand.id, 'name': obj.brand.name, 'logo': obj.brand.logo.url if obj.brand.logo else None}\
            if obj.brand else None

    def get_category(self, obj):

        categories = []
        for category in obj.category.all():
            categories.append(
                {'id': category.id, 'name': category.name}
            )
        return categories


class ShopProductVariationsSerializers(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    offer_percentage = serializers.SerializerMethodField()
    calculate_current_inventory = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'variation_title',
            'calculate_current_inventory',
            'regular_price',
            'price',
            'image',
            'offer_percentage',
        ]

    def get_image(self, obj):
        return obj.picture.url if obj.picture else None

    def get_offer_percentage(self, obj):
        if obj.regular_price and obj.price:
            offer_percentage = round(((obj.regular_price - obj.price) / obj.regular_price) * 100)
            return f'{offer_percentage}%'
        return None


class ShopProductsSimpleListSerializers(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    second_image = serializers.SerializerMethodField()
    is_in_user_wish_list = serializers.SerializerMethodField()
    is_in_user_comparison = serializers.SerializerMethodField()
    offer_percentage = serializers.SerializerMethodField()
    calculate_current_inventory = serializers.ReadOnlyField()
    variations = ShopProductVariationsSerializers(read_only=True, many=True)
    brand = BrandShopListSerializer(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id',
            'product_type',
            'name',
            'image',
            'second_image',
            'regular_price',
            'price',
            'offer_percentage',
            'is_in_user_wish_list',
            'is_in_user_comparison',
            'calculate_current_inventory',
            'variations',
            'brand',
        ]

    def get_image(self, obj):
        return obj.picture.url if obj.picture else None

    def get_second_image(self, obj):
        if ProductGallery.objects.filter(product=obj).exists():
            first_picture_of_gallery = ProductGallery.objects.filter(product=obj).first()
            return first_picture_of_gallery.picture.url if first_picture_of_gallery.picture else None
        return None

    def get_is_in_user_wish_list(self, obj):
        user = get_current_user()
        if user:
            return WishList.objects.filter(customer=user, product=obj).exists()
        else:
            return False

    def get_is_in_user_comparison(self, obj):
        user = get_current_user()
        if user:
            return Comparison.objects.filter(customer=user, product=obj).exists()
        else:
            return False

    def get_offer_percentage(self, obj):
        if obj.regular_price and obj.price:
            offer_percentage = round(((obj.regular_price - obj.price) / obj.regular_price) * 100)
            return f'{offer_percentage}%'
        return None


class ShopProductsWithCommentsListSerializers(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    second_image = serializers.SerializerMethodField()
    is_in_user_wish_list = serializers.SerializerMethodField()
    is_in_user_comparison = serializers.SerializerMethodField()
    offer_percentage = serializers.SerializerMethodField()
    get_current_inventory = serializers.ReadOnlyField()
    search_comments = serializers.SerializerMethodField()
    comments = CommentSerializer(source='confirmed_comments', read_only=True, many=True)

    class Meta:
        model = Product
        fields = [
            'id',
            'product_type',
            'name',
            'image',
            'second_image',
            'regular_price',
            'price',
            'offer_percentage',
            'is_in_user_wish_list',
            'is_in_user_comparison',
            'get_current_inventory',
            'comments',
            'search_comments',
        ]

    def get_image(self, obj):
        return obj.picture.url if obj.picture else None

    def get_second_image(self, obj):
        if ProductGallery.objects.filter(product=obj).exists():
            first_picture_of_gallery = ProductGallery.objects.filter(product=obj).first()
            return first_picture_of_gallery.picture.url if first_picture_of_gallery.picture else None
        return None

    def get_is_in_user_wish_list(self, obj):
        user = get_current_user()
        if user:
            return WishList.objects.filter(customer=user, product=obj).exists()
        else:
            return False

    def get_is_in_user_comparison(self, obj):
        user = get_current_user()
        if user:
            return Comparison.objects.filter(customer=user, product=obj).exists()
        else:
            return False

    def get_offer_percentage(self, obj):
        if obj.regular_price and obj.price:
            offer_percentage = round(((obj.regular_price - obj.price) / obj.regular_price) * 100)
            return f'{offer_percentage}%'
        return None

    def get_search_comments(self, obj):
        request = self.context.get('request')
        comment_text = request.query_params.get('global_search', None)

        if comment_text:
            filtered_comments = obj.comments.filter(text__icontains=comment_text)
        else:
            filtered_comments = obj.comments.all()
        return CommentSerializer(filtered_comments, read_only=True, many=True).data


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
    final_price = serializers.ReadOnlyField()
    rate = serializers.ReadOnlyField()
    effective_price = serializers.ReadOnlyField()
    has_offer = serializers.ReadOnlyField()
    offer_amount = serializers.ReadOnlyField()
    calculate_current_inventory = serializers.ReadOnlyField()
    gallery = ProductGallerySerializer(many=True, read_only=True)
    avails = AvailSerializer(many=True, read_only=True)
    properties = ProductPropertySerializer(many=True, read_only=True)
    image = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    brand = serializers.SerializerMethodField()
    #similar_products = serializers.SerializerMethodField()
    #similar_brand_products = serializers.SerializerMethodField()
    offer_display = serializers.ReadOnlyField()
    in_wish_list_count = serializers.ReadOnlyField()
    comments = serializers.SerializerMethodField()
    user_rate = serializers.SerializerMethodField()
    comments_count = serializers.ReadOnlyField()

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
            'calculate_current_inventory',
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
            'comments',
            'comments_count',
            #'similar_products',
            #'similar_brand_products',
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
        return {'id': obj.brand.id, 'name': obj.brand.name, 'logo': obj.brand.logo.url if obj.brand.logo  else None}\
            if obj.brand else None

    def get_category(self, obj):
        categories = []
        for category in obj.category.all():
            categories.append(
                {'id': category.id, 'name': category.name}
            )
        return categories

    #def get_similar_products(self, obj):
    #    similar_products = Product.objects.filter(
    #        Q(category=obj.category) |
    #        Q(avails__in=obj.avails) |
    #        Q(properties__in=obj.properties)
    #    ).only('id', 'name', 'picture').exclude(id=obj.id)[:10]
    #    return ShopSimilarProductsListSerializers(similar_products, many=True).data

    #def get_similar_brand_products(self, obj):
    #    similar_products = Product.objects.filter(brand=obj.brand).only('id', 'name', 'picture').exclude(id=obj.id)[:10]
    #
    #    return ShopSimilarProductsListSerializers(similar_products, many=True).data

    def get_comments(self, obj):
        comments = obj.product_comments.filter()
        return CommentSerializer(comments, many=True).data


class ShopCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'product', 'shop_order', 'reply', 'text', 'file', 'date_time']
        read_only_fields = ['id', 'date_time']

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['customer'] = get_current_user()
        return super().create(validated_data)


class ShopProductRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rate
        fields = ['id', 'product', 'level']

    def create(self, validated_data):
        user = get_current_user()
        product = validated_data.get('product')
        level = validated_data.get('level')

        rate_object, created = Rate.objects.update_or_create(
            customer=user,
            product=product,
            level=level,
        )
        return rate_object


class RootCategorySerializer(serializers.ModelSerializer):
    picture_url = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'picture_url']

    def get_picture_url(self, obj):
        return obj.picture.url if obj.picture else None
