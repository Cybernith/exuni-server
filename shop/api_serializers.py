from django.db.models import Q
from django.utils import timezone
from rest_framework import serializers

from financial_management.models import DiscountCondition, Discount, DiscountAction, DiscountConditionPriceLimit, \
    DiscountConditionPriceOver, DiscountConditionBrand, DiscountConditionProduct, DiscountConditionCategory
from helpers.functions import get_current_user
from products.models import Product, Brand, ProductGallery, Avail, ProductProperty, ProductPropertyTerm, \
    ProductAttributeTerm, ProductAttribute
from shop.models import WishList, Comparison, Cart, Comment, ShipmentAddress, ShopOrderStatusHistory, ShopOrderItem, \
    ShopOrder, Rate
from users.serializers import UserSimpleSerializer


class ShopProductPropertyTermSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductPropertyTerm
        fields = ['id', 'name', 'slug']


class ShopProductAttributeTermSerializer(serializers.ModelSerializer):
    terms = ShopProductPropertyTermSerializer(many=True)

    class Meta:
        model = ProductAttributeTerm
        fields = ['id', 'terms']


class ShopProductPropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductProperty
        fields = ['id', 'name', 'slug']


class ShopProductAttributeSerializer(serializers.ModelSerializer):
    product_property = ShopProductPropertySerializer()
    terms = ShopProductAttributeTermSerializer(many=True, source='terms.all')

    class Meta:
        model = ProductAttribute
        fields = ['id', 'product_property', 'terms']


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
    price_title = serializers.SerializerMethodField()
    regular_price_title = serializers.SerializerMethodField()

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
            'variation_title',
            'price_title',
            'regular_price_title',
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

    def get_price_title(self, obj):
        return 'قیمت در اکسونی'

    def get_regular_price_title(self, obj):
        if obj.brand and obj.brand.made_in:
            if obj.brand.made_in == 'ایران':
                return 'قیمت مصرف کننده'
        return 'قیمت محصول'


class ApiCartItemProductSerializers(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    offer_percentage = serializers.SerializerMethodField()
    brand = ApiBrandListSerializer(read_only=True)
    price_title = serializers.SerializerMethodField()
    regular_price_title = serializers.SerializerMethodField()
    same_variable_variations = serializers.SerializerMethodField()
    active_discounts = serializers.SerializerMethodField()
    calculate_current_inventory = serializers.ReadOnlyField()
    variation_of = ApiVariationListSerializers(read_only=True)
    attributes = ShopProductAttributeSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id',
            'product_type',
            'name',
            'image',
            'regular_price',
            'price',
            'offer_percentage',
            'brand',
            'variations',
            'price_title',
            'regular_price_title',
            'active_discounts',
            'same_variable_variations',
            'calculate_current_inventory',
            'variation_of',
            'attributes',
        ]

    def get_active_discounts(self, obj):
        now = timezone.now()
        discounts = Discount.objects.filter(
            is_active=True,
            start_date__lte=now,
            end_date__gte=now
        ).select_related('action').prefetch_related('conditions__category_condition__categories',
                                                    'conditions__product_condition__products',
                                                    'conditions__brand_condition__brands',
                                                    'conditions__price_over_condition',
                                                    'conditions__price_limit_condition')

        applicable_discounts = []
        for discount in discounts:
            is_applicable = False
            for condition in discount.conditions.all():
                if condition.type == DiscountCondition.CATEGORY:
                    if condition.category_condition and obj.category.filter(
                            id__in=condition.category_condition.categories.values('id')).exists():
                        is_applicable = True
                elif condition.type == DiscountCondition.BRAND:
                    if condition.brand_condition and obj.brand and obj.brand.id in\
                            condition.brand_condition.brands.values(
                            'id'):
                        is_applicable = True
                elif condition.type == DiscountCondition.PRODUCT:
                    if condition.product_condition and obj.id in condition.product_condition.products.values('id'):
                        is_applicable = True
            if is_applicable:
                applicable_discounts.append(discount)

        return DiscountSerializer(applicable_discounts, many=True, context=self.context).data

    def get_price_title(self, obj):
        return 'قیمت در اکسونی'

    def get_regular_price_title(self, obj):
        if obj.brand and obj.brand.made_in:
            if obj.brand.made_in == 'ایران':
                return 'قیمت مصرف کننده'
        return 'قیمت محصول'

    def get_image(self, obj):
        return obj.picture.url if obj.picture else None

    def get_offer_percentage(self, obj):
        if obj.regular_price and obj.price:
            offer_percentage = round(((obj.regular_price - obj.price) / obj.regular_price) * 100)
            return f'{offer_percentage}%'
        return None

    def get_same_variable_variations(self, obj):
        if obj.variation_of:
            same_variable_variations = Product.objects.filter(variation_of=obj.variation_of)
            return ApiVariationListSerializers(same_variable_variations, many=True).data
        return []


class ApiProductsListSerializers(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    second_image = serializers.SerializerMethodField()
    is_in_user_wish_list = serializers.SerializerMethodField()
    is_in_user_comparison = serializers.SerializerMethodField()
    offer_percentage = serializers.SerializerMethodField()
    calculate_current_inventory = serializers.ReadOnlyField()
    variations = ApiVariationListSerializers(read_only=True, many=True)
    brand = ApiBrandListSerializer(read_only=True)
    price_title = serializers.SerializerMethodField()
    regular_price_title = serializers.SerializerMethodField()
    active_discounts = serializers.SerializerMethodField()
    inventory_count = serializers.IntegerField(read_only=True)
    attributes = ShopProductAttributeSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id',
            'product_type',
            'name',
            'image',
            'picture',
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
            'price_title',
            'regular_price_title',
            'active_discounts',
            'inventory_count',
            'attributes',
        ]

    def get_active_discounts(self, obj):
        now = timezone.now()
        discounts = Discount.objects.filter(
            is_active=True,
            start_date__lte=now,
            end_date__gte=now
        ).select_related('action').prefetch_related('conditions__category_condition__categories',
                                                    'conditions__product_condition__products',
                                                    'conditions__brand_condition__brands',
                                                    'conditions__price_over_condition',
                                                    'conditions__price_limit_condition')

        applicable_discounts = []
        for discount in discounts:
            is_applicable = False
            for condition in discount.conditions.all():
                if condition.type == DiscountCondition.CATEGORY:
                    if condition.category_condition and obj.category.filter(
                            id__in=condition.category_condition.categories.values('id')).exists():
                        is_applicable = True
                elif condition.type == DiscountCondition.BRAND:
                    if condition.brand_condition and obj.brand and obj.brand.id in\
                            condition.brand_condition.brands.values(
                            'id'):
                        is_applicable = True
                elif condition.type == DiscountCondition.PRODUCT:
                    if condition.product_condition and obj.id in condition.product_condition.products.values('id'):
                        is_applicable = True
            if is_applicable:
                applicable_discounts.append(discount)

        return DiscountSerializer(applicable_discounts, many=True, context=self.context).data

    def get_price_title(self, obj):
        return 'قیمت در اکسونی'

    def get_regular_price_title(self, obj):
        if obj.brand and obj.brand.made_in:
            if obj.brand.made_in == 'ایران':
                return 'قیمت مصرف کننده'
        return 'قیمت محصول'

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
    product = ApiCartItemProductSerializers(read_only=True)

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
    comments = serializers.SerializerMethodField()

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
        user = get_current_user()
        if user:
            comments = obj.product_comments.filter(Q(confirmed=True) | Q(customer=user))
        else:
            comments = obj.product_comments.filter(confirmed=True)

        if comment_text:
            filtered_comments = comments.filter(text__icontains=comment_text)
        else:
            filtered_comments = comments
        return ApiCommentSerializer(filtered_comments, read_only=True, many=True).data

    def get_comments(self, obj):
        user = get_current_user()
        if user:
            comments = obj.product_comments.filter(Q(confirmed=True) | Q(customer=user))
        else:
            comments = obj.product_comments.filter(confirmed=True)
        return ApiCommentSerializer(comments, many=True).data


class ApiShipmentAddressRetrieveSerializer(serializers.ModelSerializer):
    customer = UserSimpleSerializer(read_only=True)

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = ShipmentAddress
        fields = '__all__'


class ApiOrderStatusHistorySerializer(serializers.ModelSerializer):
    new_status_display = serializers.CharField(source='get_new_status_display', read_only=True)
    previous_status_display = serializers.CharField(source='get_previous_status_display', read_only=True)

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = ShopOrderStatusHistory
        fields = ['previous_status', 'new_status', 'new_status_display', 'previous_status_display', 'changed_at',
                  'changed_by', 'note']


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
    final_amount = serializers.ReadOnlyField()

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
        user = get_current_user()
        if user:
            comments = obj.product_comments.filter(Q(confirmed=True) | Q(customer=user))
        else:
            comments = obj.product_comments.filter(confirmed=True)
        return ApiCommentSerializer(comments, many=True).data


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
    rate = serializers.ReadOnlyField()
    has_offer = serializers.ReadOnlyField()
    offer_amount = serializers.ReadOnlyField()
    calculate_current_inventory = serializers.ReadOnlyField()
    gallery = ApiProductGallerySerializer(many=True, read_only=True)
    avails = ApiAvailSerializer(many=True, read_only=True)
    properties = ApiProductPropertySerializer(many=True, read_only=True)
    image = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    brand = serializers.SerializerMethodField()
    in_wish_list_count = serializers.ReadOnlyField()
    comments = serializers.SerializerMethodField()
    user_rate = serializers.SerializerMethodField()
    comments_count = serializers.ReadOnlyField()
    variations = ApiVariationListSerializers(read_only=True, many=True)
    price_title = serializers.SerializerMethodField()
    regular_price_title = serializers.SerializerMethodField()
    offer_percentage = serializers.SerializerMethodField()
    active_discounts = serializers.SerializerMethodField()
    attributes = ShopProductAttributeSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id',
            'product_id',
            'name',
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
            'variations',
            'regular_price',
            'price',
            'price_title',
            'regular_price_title',
            'offer_percentage',
            'active_discounts',
            'attributes',
        ]

    def get_active_discounts(self, obj):
        now = timezone.now()
        discounts = Discount.objects.filter(
            is_active=True,
            start_date__lte=now,
            end_date__gte=now
        ).select_related('action').prefetch_related('conditions__category_condition__categories',
                                                    'conditions__product_condition__products',
                                                    'conditions__brand_condition__brands',
                                                    'conditions__price_over_condition',
                                                    'conditions__price_limit_condition')

        applicable_discounts = []
        for discount in discounts:
            is_applicable = False
            for condition in discount.conditions.all():
                if condition.type == DiscountCondition.CATEGORY:
                    if condition.category_condition and obj.category.filter(
                            id__in=condition.category_condition.categories.values('id')).exists():
                        is_applicable = True
                elif condition.type == DiscountCondition.BRAND:
                    if condition.brand_condition and obj.brand and obj.brand.id in\
                            condition.brand_condition.brands.values(
                            'id'):
                        is_applicable = True
                elif condition.type == DiscountCondition.PRODUCT:
                    if condition.product_condition and obj.id in condition.product_condition.products.values('id'):
                        is_applicable = True
            if is_applicable:
                applicable_discounts.append(discount)

        return DiscountSerializer(applicable_discounts, many=True, context=self.context).data

    def get_price_title(self, obj):
        return 'قیمت در اکسونی'

    def get_regular_price_title(self, obj):
        if obj.brand and obj.brand.made_in:
            if obj.brand.made_in == 'ایران':
                return 'قیمت مصرف کننده'
        return 'قیمت محصول'

    def get_offer_percentage(self, obj):
        if obj.regular_price and obj.price:
            offer_percentage = round(((obj.regular_price - obj.price) / obj.regular_price) * 100)
            return f'{offer_percentage}%'
        return None

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

    def get_comments(self, obj):
        user = get_current_user()
        if user:
            comments = obj.product_comments.filter(Q(confirmed=True) | Q(customer=user))
        else:
            comments = obj.product_comments.filter(confirmed=True)
        return ApiCommentSerializer(comments, many=True).data


class CartAddSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)

    def validate_product_id(self, value):
        from products.models import Product
        if not Product.objects.filter(id=value).exists():
            raise serializers.ValidationError("محصول مورد نظر یافت نشد.")
        return value


class ApiOrderItemSerializer(serializers.ModelSerializer):
    product = ApiProductsListSerializers(read_only=True)

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = ShopOrderItem
        fields = '__all__'


class ApiOrderStatusHistorySerializer(serializers.ModelSerializer):
    new_status_display = serializers.CharField(source='get_new_status_display', read_only=True)
    previous_status_display = serializers.CharField(source='get_previous_status_display', read_only=True)

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = ShopOrderStatusHistory
        fields = '__all__'


class ApiOrderListSerializer(serializers.ModelSerializer):
    customer = UserSimpleSerializer(read_only=True)
    items = ApiOrderItemSerializer(many=True, read_only=True)
    history = ApiOrderStatusHistorySerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    final_amount = serializers.ReadOnlyField()

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = ShopOrder
        fields = '__all__'


class DiscountConditionCategorySerializer(serializers.ModelSerializer):
    categories = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='name'
    )

    class Meta:
        model = DiscountConditionCategory
        fields = ['categories']


class DiscountConditionProductSerializer(serializers.ModelSerializer):
    products = ApiProductsListSerializers(many=True, read_only=True)

    class Meta:
        model = DiscountConditionProduct
        fields = ['products']


class DiscountConditionBrandSerializer(serializers.ModelSerializer):
    brands = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='name'
    )

    class Meta:
        model = DiscountConditionBrand
        fields = ['brands']


class DiscountConditionPriceOverSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscountConditionPriceOver
        fields = ['price_over']


class DiscountConditionPriceLimitSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscountConditionPriceLimit
        fields = ['price_limit']


class DiscountConditionSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    category_condition = DiscountConditionCategorySerializer(read_only=True)
    product_condition = DiscountConditionProductSerializer(read_only=True)
    brand_condition = DiscountConditionBrandSerializer(read_only=True)
    price_over_condition = DiscountConditionPriceOverSerializer(read_only=True)
    price_limit_condition = DiscountConditionPriceLimitSerializer(read_only=True)

    class Meta:
        model = DiscountCondition
        fields = ['type', 'type_display', 'category_condition', 'product_condition',
                  'user_condition', 'brand_condition', 'price_over_condition', 'price_limit_condition']


class DiscountActionSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_type_display', read_only=True)

    class Meta:
        model = DiscountAction
        fields = ['type', 'type_display', 'value']


class DiscountSerializer(serializers.ModelSerializer):
    conditions = DiscountConditionSerializer(many=True, read_only=True)
    action = DiscountActionSerializer(read_only=True)
    applicable_products = serializers.SerializerMethodField()

    class Meta:
        model = Discount
        fields = ['id', 'name', 'description', 'is_active', 'start_date', 'end_date',
                  'created_at', 'updated_at', 'conditions', 'action', 'applicable_products']

    def get_applicable_products(self, obj):
        conditions = obj.conditions.all()
        has_price_condition = any(
            condition.type in [DiscountCondition.PRICE_OVER, DiscountCondition.PRICE_LIMIT] for condition in conditions
        )

        if has_price_condition:
            products = Product.objects.filter(status=Product.PUBLISHED).order_by('-id')[:10]
        else:
            products = Product.objects.filter(status=Product.PUBLISHED)
            for condition in conditions:
                if condition.type == DiscountCondition.CATEGORY:
                    if condition.category_condition:
                        products = products.filter(category__in=condition.category_condition.categories.all())
                elif condition.type == DiscountCondition.BRAND:
                    if condition.brand_condition:
                        products = products.filter(brand__in=condition.brand_condition.brands.all())
                elif condition.type == DiscountCondition.PRODUCT:
                    if condition.product_condition:
                        products = products.filter(id__in=condition.product_condition.products.values('id'))

            products = products.distinct()[:10]

        return ApiProductsListSerializers(products, many=True, context=self.context).data
