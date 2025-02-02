from rest_framework import serializers

from helpers.serializers import SModelSerializer
from main.models import Business, Store, Currency, Supplier
from users.serializers import UserSimpleSerializer


class BusinessSerializer(serializers.ModelSerializer):
    created_by = UserSimpleSerializer(read_only=True)
    business_type_display = serializers.CharField(source='get_business_type_display', read_only=True)
    admin_name = serializers.CharField(source='admin.name', read_only=True)
    logo = serializers.ImageField(required=False, read_only=True)

    class Meta:
        read_only_fields = ('created_at', 'updated_at', 'business_owner_national_card_picture',
                            'products', 'customers')
        model = Business
        fields = '__all__'


class BusinessLogoUpdateSerializer(SModelSerializer):
    logo = serializers.ImageField(required=False)

    class Meta:
        read_only_fields = ('created_at', 'updated_at', 'name', 'domain_address', 'api_token', 'primary_business_color',
                            'secondary_business_color', 'theme_business_color', 'about_us', 'address', 'business_type',
                            'admin', 'phone')

        model = Business
        fields = ('id', 'logo', 'name', 'domain_address', 'api_token', 'primary_business_color',
                  'secondary_business_color', 'theme_business_color', 'about_us', 'address', 'business_type', 'admin',
                  'phone', 'created_at', 'updated_at',)



class BusinessOwnerNationalCardPictureUpdateSerializer(SModelSerializer):
    business_owner_national_card_picture = serializers.ImageField(required=False)

    class Meta:
        model = Business
        fields = ('id', 'business_owner_national_card_picture')


class StoreSerializer(serializers.ModelSerializer):
    created_by = UserSimpleSerializer(read_only=True)
    storekeeper_name = serializers.CharField(source='storekeeper.name', read_only=True)

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = Store
        fields = '__all__'


class CurrencySerializer(serializers.ModelSerializer):
    created_by = UserSimpleSerializer(read_only=True)

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = Currency
        fields = '__all__'


class SupplierSerializer(serializers.ModelSerializer):
    created_by = UserSimpleSerializer(read_only=True)
    admin_name = serializers.CharField(source='admin.name', read_only=True)

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = Supplier
        fields = '__all__'
