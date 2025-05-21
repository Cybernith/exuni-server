from rest_framework import serializers

from cms.models import HeaderElement, PopUpElement, BannerContentItem, BannerContent, ShopHomePageStory, \
    ShopHomeHighlightItem, ShopHomeHighlight


class HeaderElementSerializer(serializers.ModelSerializer):
    mobile_image_url = serializers.SerializerMethodField()
    desktop_image_url = serializers.SerializerMethodField()

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = HeaderElement
        fields = '__all__'

    def get_mobile_image_url(self, obj):
        return obj.mobile_image.url if obj.mobile_image else None

    def get_desktop_image_url(self, obj):
        return obj.desktop_image.url if obj.desktop_image else None


class PopUpElementSerializer(serializers.ModelSerializer):
    mobile_image_url = serializers.SerializerMethodField()
    desktop_image_url = serializers.SerializerMethodField()

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = PopUpElement
        fields = '__all__'

    def get_mobile_image_url(self, obj):
        return obj.mobile_image.url if obj.mobile_image else None

    def get_desktop_image_url(self, obj):
        return obj.desktop_image.url if obj.desktop_image else None


class BannerContentItemSerializer(serializers.ModelSerializer):
    mobile_image_url = serializers.SerializerMethodField()
    desktop_image_url = serializers.SerializerMethodField()

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = BannerContentItem
        fields = '__all__'

    def get_mobile_image_url(self, obj):
        return obj.mobile_image.url if obj.mobile_image else None

    def get_desktop_image_url(self, obj):
        return obj.desktop_image.url if obj.desktop_image else None


class BannerContentSerializer(serializers.ModelSerializer):
    items = BannerContentItemSerializer(many=True, read_only=True)

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = BannerContent
        fields = '__all__'


class ShopHomePageStorySerializer(serializers.ModelSerializer):
    mobile_image_url = serializers.SerializerMethodField()
    desktop_image_url = serializers.SerializerMethodField()
    video = serializers.FileField(required=False, read_only=True)

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = ShopHomePageStory
        fields = '__all__'

    def get_mobile_image_url(self, obj):
        return obj.mobile_image.url if obj.mobile_image else None

    def get_desktop_image_url(self, obj):
        return obj.desktop_image.url if obj.desktop_image else None


class ShopHomeHighlightItemSerializer(serializers.ModelSerializer):
    mobile_image_url = serializers.SerializerMethodField()
    desktop_image_url = serializers.SerializerMethodField()

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = ShopHomeHighlightItem
        fields = '__all__'

    def get_mobile_image_url(self, obj):
        return obj.mobile_image.url if obj.mobile_image else None

    def get_desktop_image_url(self, obj):
        return obj.desktop_image.url if obj.desktop_image else None


class ShopHomeHighlightSerializer(serializers.ModelSerializer):
    items = BannerContentItemSerializer(many=True, read_only=True)

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
        model = ShopHomeHighlight
        fields = '__all__'
