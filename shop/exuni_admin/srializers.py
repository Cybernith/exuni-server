from rest_framework import serializers

from financial_management.serializers import PaymentSerializer, TransactionSerializer
from shop.api_serializers import ApiShipmentAddressRetrieveSerializer, ApiOrderStatusHistorySerializer, \
    ApiCustomerShopOrderItemSerializer
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
