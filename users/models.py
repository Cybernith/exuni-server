import datetime
import random
from django.core.validators import RegexValidator
from datetime import timedelta
from django.contrib.auth.models import AbstractUser, Permission, UserManager
from django.contrib.postgres.fields.array import ArrayField
from django.db import models
from rest_framework.exceptions import ValidationError, PermissionDenied

from helpers.models import BaseModel, BaseManager
from helpers.sms import Sms


class Role(BaseModel):
    name = models.CharField(max_length=255)
    permissions = models.ManyToManyField(Permission, blank=True, related_name='roles')

    class Meta(BaseModel.Meta):
        permission_basename = 'role'
        permissions = (
            ('get.role', 'مشاهده نقش'),
            ('create.role', 'تعریف نقش'),
            ('update.role', 'ویرایش نقش'),
            ('delete.role', 'حذف نقش'),

            ('getOwn.role', 'مشاهده نقش خود'),
            ('updateOwn.role', 'ویرایش نقش خود'),
            ('deleteOwn.role', 'حذف نقش خود'),
        )


class MyUserManager(UserManager, BaseManager):
    pass


def custom_upload_to(instance, filename):
    return 'images/{filename}'.format(filename=filename)


class User(AbstractUser, BaseModel):
    superuser = models.ForeignKey('self', on_delete=models.CASCADE, related_name='users', null=True, blank=True)

    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[
            RegexValidator(
                regex='^[a-zA-Z0-9]+$',
                message='نام کاربری باید از حدوف و اعداد انگلیسی تشکیل شود'
            )
        ],
        error_messages={
            'unique': "A user with that username already exists."
        },
    )


    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=11)

    # this field is not required, because it moved to CompanyUser
    roles = models.ManyToManyField(Role, related_name='users', blank=True)

    # this field is required for cave users
    modules = ArrayField(models.CharField(max_length=30), default=list, blank=True)

    max_companies = models.IntegerField(default=0)
    max_users = models.IntegerField(default=0)

    secret_key = models.CharField(max_length=32, null=True, blank=True, default=None)

    profile_picture = models.ImageField(upload_to=custom_upload_to, null=True, blank=True, default=None)

    @property
    def name(self):
        return "{} {}".format(self.first_name, self.last_name)

    @property
    def export_name(self):
        return "{} {}".format(self.first_name, self.last_name)

    objects = MyUserManager()

    class Meta(AbstractUser.Meta):
        db_table = 'auth_user'
        default_permissions = ()

        permission_basename = 'user'
        permissions = (
            ('get.user', 'مشاهده کاربر'),
            ('create.user', 'تعریف کاربر'),
            ('update.user', 'ویرایش کاربر'),
            ('delete.user', 'حذف کاربر'),
            ('changePassword.user', 'تغییر کلمه عبور کاربران'),

            ('getOwn.user', 'مشاهده کاربران خود'),
            ('updateOwn.user', 'ویرایش کاربران خود'),
            ('deleteOwn.user', 'حذف کاربران خود'),
            ('changePasswordOwn.user', 'تغییر کلمه عبور کاربران خود'),

        )

    def get_superuser(self):
        return self.superuser or self

    def has_perm(self, permission_codename, company=None):
        return True


    def has_object_perm(self, instance: BaseModel, permission_codename, company=None, raise_exception=False):
        has_perm = self.has_perm(permission_codename, company)
        if not has_perm and instance.created_by == self:
            operation = permission_codename.split('.')[0]
            permission_codename.replace(operation, "{}Own".format(operation))
            has_perm = self.has_perm(permission_codename, company)

        if not has_perm and raise_exception:
            raise PermissionDenied()

        return has_perm


class PhoneVerification(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verificationCodes', null=True, blank=True)
    code = models.CharField(max_length=12)
    phone = models.CharField(max_length=11)

    @property
    def is_expired(self):
        return (self.created_at + timedelta(minutes=5)) < datetime.datetime.now()

    def __str__(self):
        return "user: {}, phone: {}, code: {}, datetime: {}".format(self.user, self.phone, self.code, self.created_at)

    class Meta(BaseModel.Meta):
        get_latest_by = 'id'

    @staticmethod
    def send_verification_code(username, phone):
        verify_code = random.randint(1000, 9999)
        if username and not phone:
            try:
                user = User.objects.get(username=username)
                phone_number = user.phone
                PhoneVerification.objects.create(user=user, phone=phone_number, code=verify_code)
                Sms.send(phone=phone_number, message="کد تایید شما در اکسونی: {}".format(verify_code))
                return phone_number
            except User.DoesNotExist:
                return None
        else:
            PhoneVerification.objects.create(phone=phone, code=verify_code)
            Sms.send(phone=phone, message="کد تایید شما در  اکسونی: {}".format(verify_code))
            return phone


    @staticmethod
    def check_verification_code(username, phone, code, raise_exception=False):
        try:
            if username:
                phone = User.objects.get(username=username).phone
                phone_verification = PhoneVerification.objects.filter(phone=phone, code=code).earliest()
            else:
                phone_verification = PhoneVerification.objects.filter(phone=phone, code=code).earliest()
        except PhoneVerification.DoesNotExist:
            raise ValidationError("کد تایید اشتباه است")

        if not phone_verification.is_expired:
            return code
        elif raise_exception:
            raise ValidationError("کد تایید شما منقضی شده است")

        return None


class City(BaseModel):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=255)

    class Meta(BaseModel.Meta):
        default_permissions = ()
        permissions = (
            ('create.city', 'تعریف شهر'),

            ('get.city', 'مشاهده شهر'),
            ('update.city', 'ویرایش شهر'),
            ('delete.city', 'حذف شهر'),

            ('getOwn.city', 'مشاهده شهر های خود'),
            ('updateOwn.city', 'ویرایش شهر های خود'),
            ('deleteOwn.city', 'حذف شهر های خود'),
        )

    def __str__(self):
        return self.name


class Notification(BaseModel):
    SEND_BY_USER = 'su'
    REMINDER = 'sr'
    SEND_BY_SYSTEM = 'ss'
    SEND_BY_ADMIN = 'sa'

    TYPES = (
        (SEND_BY_USER, 'ارسال شده توسط کاربر'),
        (REMINDER, 'یاداور'),
        (SEND_BY_SYSTEM, 'ارسال شده توسط سامانه'),
        (SEND_BY_ADMIN, 'ارسال شده توسط ادمین')
    )

    type = models.CharField(max_length=2, choices=TYPES)

    title = models.CharField(max_length=255, blank=True, null=True)
    # explanation is html, so should showed in <pre> tag (so we can use js editor in admin to create explanation)
    explanation = models.TextField(blank=True, null=True)
    show_pop_up = models.BooleanField(default=False)

    is_sent = models.BooleanField(default=False)

    has_schedule = models.BooleanField(default=False)
    send_date = models.DateField(blank=True, null=True)
    send_time = models.TimeField(blank=True, null=True)

    send_notification = models.BooleanField(default=False)
    notification_title = models.CharField(max_length=255, blank=True, null=True)
    notification_explanation = models.TextField(blank=True, null=True)
    notification_link = models.CharField(max_length=255, blank=True, null=True)

    send_sms = models.BooleanField(default=False)
    sms_text = models.CharField(max_length=500, blank=True, null=True)

    receivers = models.ManyToManyField(User)

    def __str__(self):
        return "{} ({})".format(self.title, self.id)

    class Meta(BaseModel.Meta):
        permissions = (
            ('send.notification', 'ارسال اعلان به سایر کاربران شرکت'),
        )

    def create_user_notifications(self):
        for receiver in self.receivers.all():
            self.userNotifications.create(
                user=receiver,
                status=UserNotification.NOT_READ,
            )
        self.is_sent = True
        self.save()


class UserNotification(BaseModel):
    PENDING = 'p'
    READ = 'r'
    NOT_READ = 'ur'

    STATUSES = (
        (PENDING, 'در انتظار ارسال'),
        (READ, 'خوانده شده'),
        (NOT_READ, 'خوانده نشده')
    )

    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name='userNotifications')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')

    status = models.CharField(choices=STATUSES, max_length=2)

    notification_status = models.CharField(choices=STATUSES, max_length=2, blank=True, null=True)
    sms_status = models.CharField(choices=STATUSES, max_length=2, blank=True, null=True)

    def __str__(self):
        return "{} -> {} ({})".format(self.notification, self.user, self.id)
