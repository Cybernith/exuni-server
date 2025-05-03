from rest_framework import serializers

from financial_management.models import Payment
from users.serializers import UserSimpleSerializer


class PaymentSerializer(serializers.ModelSerializer):
    customer = UserSimpleSerializer(read_only=True)

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = Payment
        fields = '__all__'

