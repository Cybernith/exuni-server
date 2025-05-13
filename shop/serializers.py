from rest_framework import serializers

from helpers.functions import get_current_user
from products.models import Product
from products.serializers import ProductSerializer
from shop.models import Cart, WishList, Comparison, Comment, Rate, LimitedTimeOffer, LimitedTimeOfferItems, \
    ShipmentAddress,  ShopOrder, ShopOrderItem, ShopOrderStatusHistory
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


class WishListCRUDSerializer(serializers.ModelSerializer):

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = WishList
        fields = '__all__'


class WishListRetrieveSerializer(serializers.ModelSerializer):
    customer = UserSimpleSerializer(read_only=True)
    product = ProductSerializer(read_only=True)

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = WishList
        fields = '__all__'


class ComparisonCRUDSerializer(serializers.ModelSerializer):

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = Comparison
        fields = '__all__'


class ComparisonRetrieveSerializer(serializers.ModelSerializer):
    customer = UserSimpleSerializer(read_only=True)
    product = ProductSerializer(read_only=True)

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

class PostCommentSerializer(serializers.ModelSerializer):

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = Comment
        fields = '__all__'


class RateRetrieveSerializer(serializers.ModelSerializer):
    customer = UserSimpleSerializer(read_only=True)

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = Rate
        fields = '__all__'


class RateSerializer(serializers.ModelSerializer):

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = Rate
        fields = '__all__'


class LimitedTimeOfferItemsSerializer(serializers.ModelSerializer):
    price_after_offer = serializers.ReadOnlyField()
    offer_amount = serializers.ReadOnlyField()
    offer_display = serializers.ReadOnlyField()
    product = ProductSerializer(read_only=True, many=True)

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


class ShipmentAddressCRUDSerializer(serializers.ModelSerializer):

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = ShipmentAddress
        fields = '__all__'


class ShipmentAddressRetrieveSerializer(serializers.ModelSerializer):
    customer = UserSimpleSerializer(read_only=True)

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = ShipmentAddress
        fields = '__all__'


class ShopOrderItemSerializer(serializers.ModelSerializer):

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = ShopOrderItem
        fields = '__all__'


class ShopOrderStatusHistorySerializer(serializers.ModelSerializer):
    new_status_display = serializers.CharField(source='get_new_status_display', read_only=True)

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = ShopOrderStatusHistory
        fields = '__all__'


class ShopOrderSerializer(serializers.ModelSerializer):
    customer = UserSimpleSerializer(read_only=True)
    items = ShopOrderItemSerializer(many=True, read_only=True)
    history = ShopOrderStatusHistorySerializer(many=True, read_only=True)

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = ShopOrder
        fields = '__all__'


class CustomerCartItemsSerializer(serializers.ModelSerializer):
    cart_items = CartRetrieveSerializer(many=True, read_only=True)

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = User
        fields = '__all__'


class ShopOrderItemRetrieveSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    price_sum = serializers.ReadOnlyField()

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
    wish_list_items = WishListRetrieveSerializer(many=True, read_only=True)

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = User
        fields = '__all__'


class CustomerComparisonSerializer(serializers.ModelSerializer):
    comparison_items = ComparisonRetrieveSerializer(many=True, read_only=True)

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


class ShopOrderStatusHistorySerializer(serializers.ModelSerializer):
    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = ShopOrderStatusHistory
        fields = ['previous_status', 'new_status', 'changed_at', 'changed_by', 'note']


class CustomerProductRateSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    rate = serializers.IntegerField(allow_null=True)


class CartInputSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(default=1)


class WishlistInputSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()


class CompareItemInputSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()


class SyncAllDataSerializer(serializers.Serializer):
    cart_items = CartInputSerializer(many=True, required=False)
    wishlist_items = WishlistInputSerializer(many=True, required=False)
    comparison_items = CompareItemInputSerializer(many=True, required=False)


class OrderProductsSimpleListSerializers(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    offer_percentage = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'image',
        ]

    def get_image(self, obj):
        return obj.picture.url if obj.picture else None


class UserCommentCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'text', 'file', 'date_time']
        read_only_fields = ['id', 'date_time']


class UserRateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Rate
        fields = ['id', 'level']

class UserCommentProductsSimpleListSerializers(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    products_rates = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'image',
            'comments',
        ]

    def get_image(self, obj):
        return obj.picture.url if obj.picture else None

    def get_comments(self, obj):
        return UserCommentCommentSerializer(obj.product_comments.filter(customer=get_current_user()), many=True).data

    def get_user_rate(self, obj):
        return UserRateSerializer(obj.rates.filter(customer=get_current_user()), many=True).data


class CustomerShopOrderItemSimpleSerializer(serializers.ModelSerializer):
    product = OrderProductsSimpleListSerializers(read_only=True)

    class Meta:
        model = ShopOrderItem
        fields = ('id', 'product', 'price', 'product_quantity')


class CustomerShopOrderSimpleSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source='get_status_display', read_only=True)
    customer = UserSimpleSerializer(read_only=True)
    shipment_address = ShipmentAddressRetrieveSerializer(read_only=True)
    history = ShopOrderStatusHistorySerializer(many=True, read_only=True)
    items = CustomerShopOrderItemSimpleSerializer(many=True, read_only=True)

    class Meta:
        model = ShopOrder
        fields = '__al__'

