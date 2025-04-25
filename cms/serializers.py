from rest_framework import serializers

from cms.models import HeaderElement, PopUpElement, BannerContentItem, BannerContent, ShopHomePageStory


class HeaderElementSerializer(serializers.ModelSerializer):
    mobile_image = serializers.ImageField(required=False, read_only=True)
    desktop_image = serializers.ImageField(required=False, read_only=True)

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = HeaderElement
        fields = '__all__'


class PopUpElementSerializer(serializers.ModelSerializer):
    mobile_image = serializers.ImageField(required=False, read_only=True)
    desktop_image = serializers.ImageField(required=False, read_only=True)

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = PopUpElement
        fields = '__all__'


class BannerContentItemSerializer(serializers.ModelSerializer):
    mobile_image = serializers.ImageField(required=False, read_only=True)
    desktop_image = serializers.ImageField(required=False, read_only=True)

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = BannerContentItem
        fields = '__all__'


class BannerContentSerializer(serializers.ModelSerializer):
    items = BannerContentItemSerializer(many=True, read_only=True)

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = BannerContent
        fields = '__all__'


class ShopHomePageStorySerializer(serializers.ModelSerializer):
    mobile_image = serializers.ImageField(required=False, read_only=True)
    desktop_image = serializers.ImageField(required=False, read_only=True)
    video = serializers.FileField(required=False, read_only=True)

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = ShopHomePageStory
        fields = '__all__'
