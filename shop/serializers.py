from rest_framework import serializers

from products.serializers import ProductSerializer
from shop.models import Cart, WishList, Comparison, Comment, Rate, LimitedTimeOffer, LimitedTimeOfferItems, \
    ShipmentAddress, Payment, ShopOrder, ShopOrderItem
from users.models import User
from users.serializers import UserSimpleSerializer


class CartCRUDSerializer(serializers.ModelSerializer):

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = Cart
        fields = '__all__'


class CartRetrieveSerializer(serializers.ModelSerializer):
    customer = UserSimpleSerializer(read_only=True)
    product = ProductSerializer(read_only=True)

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = Cart
        fields = '__all__'


class WishListSerializer(serializers.ModelSerializer):
    customer = UserSimpleSerializer(read_only=True)

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = WishList
        fields = '__all__'


class ComparisonSerializer(serializers.ModelSerializer):
    customer = UserSimpleSerializer(read_only=True)
    cart_items = ProductSerializer(many=True, read_only=True)

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = Comparison
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    customer = UserSimpleSerializer(read_only=True)

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = Comment
        fields = '__all__'


class RateSerializer(serializers.ModelSerializer):
    customer = UserSimpleSerializer(read_only=True)

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = Rate
        fields = '__all__'


class LimitedTimeOfferItemsSerializer(serializers.ModelSerializer):

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = LimitedTimeOfferItems
        fields = '__all__'


class LimitedTimeOfferSerializer(serializers.ModelSerializer):
    customer = UserSimpleSerializer(read_only=True)
    items = LimitedTimeOfferItemsSerializer(read_only=True)

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = LimitedTimeOffer
        fields = '__all__'


class ShipmentAddressSerializer(serializers.ModelSerializer):
    customer = UserSimpleSerializer(read_only=True)

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = ShipmentAddress
        fields = '__all__'


class PaymentSerializer(serializers.ModelSerializer):
    customer = UserSimpleSerializer(read_only=True)

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = Payment
        fields = '__all__'


class ShopOrderItemSerializer(serializers.ModelSerializer):

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = ShopOrderItem
        fields = '__all__'


class ShopOrderSerializer(serializers.ModelSerializer):
    customer = UserSimpleSerializer(read_only=True)
    items = ShopOrderItemSerializer(many=True, read_only=True)

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = ShopOrder
        fields = '__all__'


class CartItemsRetrieveSerializer(serializers.ModelSerializer):
    cart_items = ProductSerializer(read_only=True)

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = Cart
        fields = '__all__'


class CustomerCartItemsSerializer(serializers.ModelSerializer):
    cart_items = CartItemsRetrieveSerializer(many=True, read_only=True)

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = User
        fields = '__all__'


class ShopOrderItemRetrieveSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = ShopOrderItem
        fields = '__all__'


class CustomerShopOrdersRetrieveSerializer(serializers.ModelSerializer):
    customer = UserSimpleSerializer(read_only=True)
    items = ShopOrderItemRetrieveSerializer(read_only=True)

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = ShopOrder
        fields = '__all__'


class CustomerShopOrdersSerializer(serializers.ModelSerializer):
    shop_order = CustomerShopOrdersRetrieveSerializer(many=True, read_only=True)

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = User
        fields = '__all__'


class CustomerWishListSerializer(serializers.ModelSerializer):
    wish_list_items = WishListSerializer(many=True, read_only=True)

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = User
        fields = '__all__'


class CustomerComparisonSerializer(serializers.ModelSerializer):
    comparison_items = ComparisonSerializer(many=True, read_only=True)

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = User
        fields = '__all__'


class CommentRepliesSerializer(serializers.ModelSerializer):
    customer = UserSimpleSerializer(read_only=True)
    replies = CommentSerializer(many=True, read_only=True)

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = Comment
        fields = '__all__'

