from django.contrib.auth import get_user_model
from rest_framework import serializers

from financial_management.models import Payment, Wallet, DiscountConditionCategory, DiscountConditionProduct, \
    DiscountConditionUser, DiscountConditionBrand, DiscountConditionPriceOver, DiscountConditionPriceLimit, \
    DiscountCondition, DiscountAction, Discount
from helpers.functions import get_current_user
from helpers.serializers import SModelSerializer
from products.models import Product
from shop.api_serializers import ApiProductsListSerializers
from users.models import User


class UserSimpleSerializer(SModelSerializer):
    name = serializers.SerializerMethodField()
    profile_picture = serializers.ImageField(read_only=True)
    cover_picture = serializers.ImageField(read_only=True)

    def get_name(self, obj: User):
        if obj.first_name and obj.last_name:
            return obj.first_name + ' ' + obj.last_name
        else:
            return obj.username

    class Meta:
        model = get_user_model()
        fields = ('id', 'first_name', 'last_name',  'username', 'mobile_number', 'name',
                  'profile_picture', 'cover_picture', 'address', 'postal_code')


class PaymentSerializer(serializers.ModelSerializer):
    customer = UserSimpleSerializer(read_only=True)

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = Payment
        fields = '__all__'


class CurrentUserWalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['balance']
        read_only_fields = ['balance']


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
