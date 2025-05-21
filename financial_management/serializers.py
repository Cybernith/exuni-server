from django.contrib.auth import get_user_model
from rest_framework import serializers

from financial_management.models import Payment, Wallet
from helpers.serializers import SModelSerializer
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

