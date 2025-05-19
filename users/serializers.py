from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from financial_management.serializers import CurrentUserWalletSerializer
from helpers.functions import get_current_user
from helpers.serializers import SModelSerializer
from main.models import Business
from subscription.serializers import WalletSerializer
from users.models import Role, User, City, UserNotification, Notification


class RoleSerializer(SModelSerializer):
    permissions = serializers.PrimaryKeyRelatedField(many=True, queryset=Permission.objects.all())

    class Meta:
        model = Role
        fields = '__all__'
        read_only_fields = ('id', 'company', 'created_at', 'updated_at')


class ContentTypeSerializer(SModelSerializer):
    class Meta:
        model = ContentType
        fields = '__all__'


class PermissionListSerializer(SModelSerializer):
    content_type = ContentTypeSerializer()
    contentType = content_type

    class Meta:
        model = Permission
        fields = '__all__'


class RoleWithPermissionListSerializer(SModelSerializer):
    permissions = PermissionListSerializer(many=True)

    class Meta:
        model = Role
        fields = '__all__'


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


class UserListSerializer(SModelSerializer):
    name = serializers.SerializerMethodField()
    business_token = serializers.SerializerMethodField()
    profile_picture = serializers.ImageField(read_only=True)

    def get_name(self, obj: User):
        if obj.first_name and obj.last_name:
            return obj.first_name + ' ' + obj.last_name
        else:
            return obj.username

    def get_business_token(self, obj: User):
        if obj.user_type == User.BUSINESS_OWNER and Business.objects.filter(admin=obj).exists():
            return Business.objects.get(admin=obj).api_token
        else:
            return ''

    class Meta:
        model = get_user_model()
        exclude = ('password', 'secret_key', '_wallet')


class UserRetrieveSerializer(UserListSerializer):
    profile_picture = serializers.ImageField(read_only=True)
    wallet = serializers.SerializerMethodField()

    def get_wallet(self, obj: User):
        return CurrentUserWalletSerializer(obj.exuni_wallet).data

    class Meta(UserListSerializer.Meta):
        pass


class UserCreateSerializer(SModelSerializer):
    password = serializers.CharField(default=None, allow_null=True, write_only=True)
    token = serializers.SerializerMethodField()

    def get_token(self, obj: User):
        token, created = Token.objects.get_or_create(user=obj)
        return token.key

    class Meta:
        model = get_user_model()
        fields = ('username', 'first_name', 'last_name', 'mobile_number', 'password', 'token')

    def create(self, validated_data):
        user = super().create(validated_data)
        password = validated_data.get('password')
        user.set_password(password)
        user.save()
        return user


class UserUpdateSerializer(SModelSerializer):
    profile_picture = serializers.ImageField(required=False)
    cover_picture = serializers.ImageField(required=False)

    class Meta:
        model = get_user_model()
        fields = ('first_name', 'last_name', 'profile_picture', 'cover_picture')


class CitySerializer(SModelSerializer):
    class Meta:
        model = City
        fields = '__all__'


        fields = ('id', 'company_name', 'status')


class NotificationSerializer(SModelSerializer):

    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class UserNotificationSerializer(SModelSerializer):
    user = serializers.CharField(source='user.name')
    created_by = serializers.CharField(source='created_by.name', read_only=True)
    status = serializers.CharField(source='get_status_display')
    title = serializers.CharField(source='notification.title')
    explanation = serializers.CharField(source='notification.explanation')
    status_codename = serializers.CharField(source='status')
    notification = NotificationSerializer(read_only=True)

    class Meta:
        model = UserNotification
        fields = ('id', 'title', 'created_by', 'explanation', 'status', 'created_at',
                  'status_codename', 'user', 'notification')


class SendNotificationSerializer(SModelSerializer):
    userNotifications = UserNotificationSerializer(many=True, read_only=True)

    class Meta:
        model = Notification
        fields = (
            'id', 'title', 'explanation', 'show_pop_up', 'has_schedule', 'send_date', 'send_time', 'receivers',
            'userNotifications', 'created_at', 'forwarder_company'
        )
        read_only_fields = ('created_at', 'updated_at')

    def validate_receivers(self, value):
        return value


class ReminderNotificationSerializer(SModelSerializer):
    class Meta:
        model = Notification
        fields = ('id', 'title', 'explanation', 'send_date', 'send_time')

    def validate_receivers(self, value):
        if value:
            user = get_current_user()
            is_valid = user.active_company.filter(users__in=value).count() == len(value)
            if not is_valid:
                raise serializers.ValidationError("کاربران انتخاب شده معتبر نمی باشند")
        return value


class CurrentUserNotificationSerializer(SModelSerializer):
    unread_notifications_count = serializers.SerializerMethodField()
    pop_up_notifications = serializers.SerializerMethodField()

    def get_pop_up_notifications(self, obj: User):
        qs = obj.notifications.exclude(status=UserNotification.READ).filter(notification__show_pop_up=True)
        return UserNotificationSerializer(qs, many=True).data

    def get_unread_notifications_count(self, obj: User):
        return obj.notifications.exclude(status=UserNotification.READ).count()

    class Meta:
        model = get_user_model()
        fields = ('id', 'unread_notifications_count', 'pop_up_notifications')


