from rest_framework import serializers

from helpers.functions import get_current_user
from products.models import Product, Brand, ProductGallery, Avail, ProductProperty
from shop.models import WishList, Comparison, Cart, Comment, ShipmentAddress, ShopOrderStatusHistory, ShopOrderItem, \
    ShopOrder, Rate
from users.serializers import UserSimpleSerializer


class ApiBrandListSerializer(serializers.ModelSerializer):
    logo_url = serializers.SerializerMethodField()

    class Meta:
        model = Brand
        fields = ('id', 'name', 'logo_url')

    def get_logo_url(self, obj):
        return obj.logo.url if obj.logo else None


class ApiVariationListSerializers(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    second_image = serializers.SerializerMethodField()
    is_in_user_wish_list = serializers.SerializerMethodField()
    is_in_user_comparison = serializers.SerializerMethodField()
    offer_percentage = serializers.SerializerMethodField()
    calculate_current_inventory = serializers.ReadOnlyField()
    brand = ApiBrandListSerializer(read_only=True)

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
            'brand',
            'postal_weight',
            'length',
            'width',
            'height',
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


class ApiProductsListSerializers(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    second_image = serializers.SerializerMethodField()
    is_in_user_wish_list = serializers.SerializerMethodField()
    is_in_user_comparison = serializers.SerializerMethodField()
    offer_percentage = serializers.SerializerMethodField()
    calculate_current_inventory = serializers.ReadOnlyField()
    variations = ApiVariationListSerializers(read_only=True, many=True)
    brand = ApiBrandListSerializer(read_only=True)

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
            'postal_weight',
            'length',
            'width',
            'height',
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


class ApiCartRetrieveSerializer(serializers.ModelSerializer):
    customer = UserSimpleSerializer(read_only=True)
    product = ApiProductsListSerializers(read_only=True)

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = Cart
        fields = '__all__'


class ApiWishListRetrieveSerializer(serializers.ModelSerializer):
    customer = UserSimpleSerializer(read_only=True)
    product = ApiProductsListSerializers(read_only=True)

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = WishList
        fields = '__all__'


class ApiComparisonRetrieveSerializer(serializers.ModelSerializer):
    customer = UserSimpleSerializer(read_only=True)
    product = ApiProductsListSerializers(read_only=True)

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = Comparison
        fields = '__all__'


class ApiCommentSerializer(serializers.ModelSerializer):
    customer = UserSimpleSerializer(read_only=True)

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = Comment
        fields = '__all__'


class ApiProductsWithCommentsListSerializers(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    second_image = serializers.SerializerMethodField()
    is_in_user_wish_list = serializers.SerializerMethodField()
    is_in_user_comparison = serializers.SerializerMethodField()
    offer_percentage = serializers.SerializerMethodField()
    calculate_current_inventory = serializers.ReadOnlyField()
    variations = ApiVariationListSerializers(read_only=True, many=True)
    brand = ApiBrandListSerializer(read_only=True)
    search_comments = serializers.SerializerMethodField()
    comments = ApiCommentSerializer(source='confirmed_comments', read_only=True, many=True)

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
        return ApiCommentSerializer(filtered_comments, read_only=True, many=True).data


class ApiShipmentAddressRetrieveSerializer(serializers.ModelSerializer):
    customer = UserSimpleSerializer(read_only=True)

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = ShipmentAddress
        fields = '__all__'


class ApiOrderStatusHistorySerializer(serializers.ModelSerializer):
    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = ShopOrderStatusHistory
        fields = ['previous_status', 'new_status', 'changed_at', 'changed_by', 'note']


class ApiCustomerShopOrderItemSerializer(serializers.ModelSerializer):
    product = ApiProductsListSerializers(read_only=True)

    class Meta:
        model = ShopOrderItem
        fields = ('id', 'product', 'price', 'product_quantity')


class ApiCustomerShopOrderSimpleSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source='get_status_display', read_only=True)
    customer = UserSimpleSerializer(read_only=True)
    shipment_address = ApiShipmentAddressRetrieveSerializer(read_only=True)
    history = ApiOrderStatusHistorySerializer(many=True, read_only=True)
    items = ApiCustomerShopOrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = ShopOrder
        fields = '__all__'


class ApiUserRateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Rate
        fields = ['id', 'level']


class ApiUserCommentProductsSimpleListSerializers(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    second_image = serializers.SerializerMethodField()
    is_in_user_wish_list = serializers.SerializerMethodField()
    is_in_user_comparison = serializers.SerializerMethodField()
    offer_percentage = serializers.SerializerMethodField()
    calculate_current_inventory = serializers.ReadOnlyField()
    variations = ApiVariationListSerializers(read_only=True, many=True)
    brand = ApiBrandListSerializer(read_only=True)
    comments = serializers.SerializerMethodField()
    products_rates = serializers.SerializerMethodField()

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
            'comments',
            'products_rates',
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

    def get_comments(self, obj):
        return ApiCommentSerializer(obj.product_comments.filter(customer=get_current_user()), many=True).data

    def get_user_rate(self, obj):
        return ApiUserRateSerializer(obj.rates.filter(customer=get_current_user()), many=True).data


class ApiProductGallerySerializer(serializers.ModelSerializer):

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = ProductGallery
        fields = '__all__'


class ApiAvailSerializer(serializers.ModelSerializer):

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = Avail
        fields = '__all__'


class ApiProductPropertySerializer(serializers.ModelSerializer):
    created_by = UserSimpleSerializer(read_only=True)

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = ProductProperty
        fields = '__all__'


class ApiProductDetailSerializers(serializers.ModelSerializer):
    final_price = serializers.ReadOnlyField()
    rate = serializers.ReadOnlyField()
    effective_price = serializers.ReadOnlyField()
    has_offer = serializers.ReadOnlyField()
    offer_amount = serializers.ReadOnlyField()
    calculate_current_inventory = serializers.ReadOnlyField()
    gallery = ApiProductGallerySerializer(many=True, read_only=True)
    avails = ApiAvailSerializer(many=True, read_only=True)
    properties = ApiProductPropertySerializer(many=True, read_only=True)
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
        return ApiCommentSerializer(comments, many=True).data


