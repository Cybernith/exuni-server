from rest_framework import serializers

from helpers.serializers import SModelSerializer
from server.settings import BASE_DIR, SERVER_URL
from shop.models import Cart, WishList, Comparison, Comment, Rate, LimitedTimeOffer, LimitedTimeOfferItems, \
    ShipmentAddress, Payment, ShopOrder, ShopOrderItem
from users.serializers import UserSimpleSerializer
from django.db.models import Sum, IntegerField, Q, Count, F


class CartSerializer(serializers.ModelSerializer):
    customer = UserSimpleSerializer(read_only=True)

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
    limited_time_offer = LimitedTimeOfferItemsSerializer(read_only=True)

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
    shop_order = ShopOrderItemSerializer(read_only=True)

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = ShopOrder
        fields = '__all__'

