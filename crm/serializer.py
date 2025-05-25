from django.shortcuts import get_object_or_404
from rest_framework import serializers

from crm.models import ShopProductViewLog, UserNotification, Notification, InventoryReminder
from products.models import Product
from products.shop.serializers import ShopProductsListSerializers
from users.models import User


class ShopProductViewLogCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopProductViewLog
        field = ['ip_address', 'referer', 'device_type', 'user_agent']

    def create(self, validated_data):
        request = self.context['request']
        product = get_object_or_404(Product, pk=self.context['view'].kwargs['product_id'])
        return ShopProductViewLog.objects.create(
            product=product,
            user=request.user if request.user.is_authenticated else None,
            **validated_data
        )


class ShopProductViewLogSerializer(serializers.ModelSerializer):
    device_type = serializers.CharField(source='get_device_type_display', read_only=True)
    user_name = serializers.CharField(source='user.name', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = ShopProductViewLog
        fields = '__all__'


class NotificationCreateSerializer(serializers.Serializer):
    exclude = serializers.BooleanField(default=False)
    send_sms = serializers.BooleanField(default=False)
    sms_text = serializers.CharField(max_length=255)
    send_datetime = serializers.DateTimeField()
    notification_title = serializers.CharField(max_length=255)
    notification_explanation = serializers.CharField()
    notification_link = serializers.URLField()
    users = serializers.ListField(
        child=serializers.IntegerField(), write_only=True
    )
    product = serializers.IntegerField()

    seen_product = serializers.IntegerField()
    seen_category = serializers.IntegerField()
    searched_about = serializers.CharField()
    purchased_product = serializers.IntegerField()
    more_than_amount = serializers.IntegerField()

    def validate_users(self, value):
        if User.objects.filter(id__in=value).count() != len(set(value)):
            raise serializers.ValidationError("برخی از شناسه‌های کاربر نامعتبر هستند.")
        return value

    def validate_products(self, value):
        if Product.objects.filter(id=value).exists():
            raise serializers.ValidationError("شناسه‌ محصول نامعتبر است.")
        return value

    def validate_seen_product(self, value):
        if Product.objects.filter(id=value).exists():
            raise serializers.ValidationError("شناسه‌ محصول بازدید شده نامعتبر است.")
        return value

    def validate_purchased_product(self, value):
        if Product.objects.filter(id=value).exists():
            raise serializers.ValidationError("شناسه‌ محصول خریداری شده نامعتبر است.")
        return value

    def validate_seen_category(self, value):
        if Product.objects.filter(id=value).exists():
            raise serializers.ValidationError("شناسه‌ دسته بندی بازدید شده نامعتبر است.")
        return value


class NotificationRetrieveSerializer(serializers.ModelSerializer):
    product = ShopProductsListSerializers(read_only=True)
    sort_display = serializers.CharField(source='get_sort_display')
    type_display = serializers.CharField(source='get_type_display')
    image = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = ['id', 'send_datetime', 'notification_title',
                 'notification_explanation', 'notification_link',
                 'notification_btn_title', 'sort_display', 'type_display', 'product', 'image']

    def get_image(self, obj):
        return obj.picture.url if obj.picture else None


class UserNotificationRetrieveSerializer(serializers.ModelSerializer):
    notification = NotificationRetrieveSerializer(read_only=True)

    class Meta:
        model = UserNotification
        fields = ['id', 'notification', 'notification_status', 'sms_status']


class InventoryReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryReminder
        fields = ['id', 'product']
