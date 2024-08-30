from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from helpers.functions import get_current_user
from helpers.serializers import MModelSerializer
from users.models import Role, User, City, UserNotification, Notification


class RoleSerializer(MModelSerializer):
    permissions = serializers.PrimaryKeyRelatedField(many=True, queryset=Permission.objects.all())

    class Meta:
        model = Role
        fields = '__all__'
        read_only_fields = ('id', 'company', 'created_at', 'updated_at')


class ContentTypeSerializer(MModelSerializer):
    class Meta:
        model = ContentType
        fields = '__all__'


class PermissionListSerializer(MModelSerializer):
    content_type = ContentTypeSerializer()
    contentType = content_type

    class Meta:
        model = Permission
        fields = '__all__'


class RoleWithPermissionListSerializer(MModelSerializer):
    permissions = PermissionListSerializer(many=True)

    class Meta:
        model = Role
        fields = '__all__'


class UserSimpleSerializer(MModelSerializer):
    name = serializers.SerializerMethodField()
    profile_picture = serializers.ImageField(read_only=True)

    def get_name(self, obj: User):
        return obj.first_name + ' ' + obj.last_name

    class Meta:
        model = get_user_model()
        fields = ('id', 'first_name', 'last_name', 'name', 'username', 'phone', 'profile_picture')


class UserListSerializer(MModelSerializer):
    name = serializers.SerializerMethodField()
    has_two_factor_authentication = serializers.SerializerMethodField()
    unread_notifications_count = serializers.SerializerMethodField()
    pop_up_notifications = serializers.SerializerMethodField()
    profile_picture = serializers.ImageField(read_only=True)

    def get_pop_up_notifications(self, obj: User):
        qs = obj.notifications.exclude(status=UserNotification.READ).filter(notification__show_pop_up=True)
        return UserNotificationSerializer(qs, many=True).data

    def get_unread_notifications_count(self, obj: User):
        return obj.notifications.exclude(status=UserNotification.READ).count()

    def get_name(self, obj: User):
        return obj.first_name + ' ' + obj.last_name

    def get_has_two_factor_authentication(self, obj: User):
        return obj.secret_key is not None

    class Meta:
        model = get_user_model()
        exclude = ('password', 'secret_key')


class UserRetrieveSerializer(UserListSerializer):
    profile_picture = serializers.ImageField(read_only=True)

    class Meta(UserListSerializer.Meta):
        pass


class UserCreateSerializer(MModelSerializer):
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


class UserUpdateSerializer(MModelSerializer):
    profile_picture = serializers.ImageField(required=False)

    class Meta:
        model = get_user_model()
        fields = ('first_name', 'last_name', 'profile_picture', 'cover_picture')


class CitySerializer(MModelSerializer):
    class Meta:
        model = City
        fields = '__all__'


        fields = ('id', 'company_name', 'status')


class NotificationSerializer(MModelSerializer):

    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class UserNotificationSerializer(MModelSerializer):
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


class SendNotificationSerializer(MModelSerializer):
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


class ReminderNotificationSerializer(MModelSerializer):
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


class CurrentUserNotificationSerializer(MModelSerializer):
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


