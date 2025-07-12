from rest_framework import serializers

from financial_management.serializers import PaymentSerializer, TransactionSerializer
from helpers.functions import get_current_user
from products.models import Product
from products.serializers import CategorySerializer
from shop.api_serializers import ApiShipmentAddressRetrieveSerializer, ApiOrderStatusHistorySerializer, \
    ApiCustomerShopOrderItemSerializer, ApiVariationListSerializers, ApiBrandListSerializer, ApiProductGallerySerializer
from shop.models import ShopOrder
from shop.serializers import ShopOrderStatusHistorySerializer
from users.serializers import UserSimpleSerializer


class AdminShopOrderSimpleSerializer(serializers.ModelSerializer):
    customer = UserSimpleSerializer(read_only=True)
    shipment_address = ApiShipmentAddressRetrieveSerializer(read_only=True)
    final_amount = serializers.ReadOnlyField()
    payment_display = serializers.ReadOnlyField()
    printed_user = serializers.CharField(source='print_by.username', read_only=True)

    class Meta:
        model = ShopOrder
        fields = '__all__'


class AdminShopOrderDetailSerializer(serializers.ModelSerializer):
    customer = UserSimpleSerializer(read_only=True)
    shipment_address = ApiShipmentAddressRetrieveSerializer(read_only=True)
    history = ShopOrderStatusHistorySerializer(many=True, read_only=True)
    final_amount = serializers.ReadOnlyField()
    payment_display = serializers.ReadOnlyField()
    printed_user = serializers.CharField(source='print_by.username', read_only=True)
    items = ApiCustomerShopOrderItemSerializer(many=True, read_only=True)
    bank_payment = PaymentSerializer(read_only=True)
    transaction = TransactionSerializer(many=True, read_only=True)

    class Meta:
        model = ShopOrder
        fields = '__all__'


class AdminProductsListSerializers(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    offer_percentage = serializers.SerializerMethodField()
    calculate_current_inventory = serializers.ReadOnlyField()
    brand = ApiBrandListSerializer(read_only=True)
    price_title = serializers.SerializerMethodField()
    regular_price_title = serializers.SerializerMethodField()
    inventory_count = serializers.IntegerField(read_only=True)
    variation_of_name = serializers.CharField(source='variation_of.name', read_only=True)
    currency_name = serializers.CharField(source='currency.name', read_only=True)
    gallery = ApiProductGallerySerializer(many=True, read_only=True)
    category = CategorySerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'image',
            'regular_price',
            'price',
            'offer_percentage',
            'calculate_current_inventory',
            'variations',
            'brand',
            'status',
            'price_title',
            'regular_price_title',
            'inventory_count',
            'sixteen_digit_code',
            'variation_of_name',
            'product_type',
            'currency_name',
            'gallery',
            'category',

        ]

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

