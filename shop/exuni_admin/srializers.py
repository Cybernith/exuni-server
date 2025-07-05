from rest_framework import serializers

from shop.api_serializers import ApiShipmentAddressRetrieveSerializer, ApiOrderStatusHistorySerializer, \
    ApiCustomerShopOrderItemSerializer
from shop.models import ShopOrder
from users.serializers import UserSimpleSerializer


class AdminShopOrderSimpleSerializer(serializers.ModelSerializer):
    customer = UserSimpleSerializer(read_only=True)
    shipment_address = ApiShipmentAddressRetrieveSerializer(read_only=True)
    history = ApiOrderStatusHistorySerializer(many=True, read_only=True)
    items = ApiCustomerShopOrderItemSerializer(many=True, read_only=True)
    final_amount = serializers.ReadOnlyField()
    payment_display = serializers.ReadOnlyField()

    class Meta:
        model = ShopOrder
        fields = '__all__'
