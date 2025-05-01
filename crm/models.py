from django.db import models

from helpers.models import TimeStampedModel

from user_agents import parse as user_agent_parse
from helpers.sms import Sms


class UserAgentModel(models.Model):
    DESKTOP = 'd'
    MOBILE = 'm'
    TABLET = 't'
    BOT = 'b'
    OTHER = 'o'

    DEVICE_TYPES = (
        (DESKTOP, 'دسکتاپ'),
        (MOBILE, 'موبایل'),
        (TABLET, 'تبلت'),
        (BOT, 'روبات'),
        (OTHER, 'متفرقه'),
    )

    user_agent = models.TextField()
    device_type = models.CharField(max_length=1, choices=DEVICE_TYPES, default=OTHER)
    browser_type = models.CharField(max_length=100, blank=True, null=True)
    browser_version = models.CharField(max_length=100, blank=True, null=True)
    os_type = models.CharField(max_length=100, blank=True, null=True)
    os_version = models.CharField(max_length=100, blank=True, null=True)
    device_family = models.CharField(max_length=100, blank=True, null=True)
    is_touch_device = models.BooleanField(default=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)

    @property
    def user_agent_object(self):
        return user_agent_parse(self.user_agent or '')

    @property
    def get_browser_type(self):
        return self.user_agent_object.browser.family

    @property
    def get_browser_version(self):
        version = self.user_agent_object.browser.version
        return '.'.join(str(version_value) for version_value in version) if version else None

    @property
    def get_os_type(self):
        return self.user_agent_object.os.family

    @property
    def get_os_version(self):
        version = self.user_agent_object.os.version
        return '.'.join(str(version_value) for version_value in version) if version else None

    @property
    def get_device_family(self):
        return self.user_agent_object.device.version or None

    @property
    def get_user_device(self):
        if self.user_agent_object.is_mobile:
            return self.MOBILE
        elif self.user_agent_object.is_pc:
            return self.DESKTOP
        elif self.user_agent_object.is_tablet:
            return self.TABLET
        elif self.user_agent_object.is_bot:
            return self.BOT
        else:
            return self.OTHER

    @property
    def get_is_touch_device(self):
        return self.user_agent_object.is_touch_capable

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.id and self.user_agent:
            self.device_type = self.get_user_device
            self.browser_type = self.get_browser_type
            self.browser_version = self.get_browser_version
            self.os_type = self.get_os_type
            self.os_version = self.get_os_version
            self.device_family = self.get_device_family
            self.is_touch_device = self.get_is_touch_device

        super().save(*args, **kwargs)


class ShopProductViewLog(TimeStampedModel, UserAgentModel):
    product = models.ForeignKey(
        'products.Product',
        related_name='views_log',
        on_delete=models.CASCADE,
        db_index=True
    )
    category = models.ForeignKey(
        'products.Category',
        related_name='views_log',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        db_index=True
    )
    user = models.ForeignKey(
        'users.User',
        related_name='product_views',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    referer = models.URLField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product', 'created_at']),
            models.Index(fields=['user', 'created_at'])
        ]

    def __str__(self):
        return f"view of product {self.product.name} by {self.user.name or 'guest'} at {self.created_at}"


class SearchLog(TimeStampedModel, UserAgentModel):

    PRODUCT = 'product'
    CATEGORY = 'category'
    BRAND = 'brand'
    AVAIL = 'avail'
    PROPERTY = 'property'
    RAW_TEXT = 'raw'

    SEARCH_TYPES = (
        (PRODUCT, 'محصول'),
        (CATEGORY, 'دسته بندی'),
        (BRAND, 'برند'),
        (AVAIL, 'فایده'),
        (PROPERTY, 'خصوصیت کالا'),
        (RAW_TEXT, 'متن'),
    )

    user = models.ForeignKey(
        'users.User',
        related_name='search_logs',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    query_value = models.CharField(max_length=255)
    search_type = models.CharField(max_length=8, choices=SEARCH_TYPES, default=RAW_TEXT)

    product = models.ForeignKey(
        'products.Product',
        related_name='searches_log',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    category = models.ForeignKey(
        'products.Category',
        related_name='searches_log',
        on_delete=models.CASCADE,
        null=True,
        blank=True,

    )
    avail = models.ForeignKey(
        'products.Avail',
        related_name='searches_log',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    property = models.ForeignKey(
        'products.ProductProperty',
        related_name='searches_log',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['query_value']),
            models.Index(fields=['user', 'created_at'])
        ]

    def __str__(self):
        return f"{self.user.name or 'guest'} search about ''' {self.query_value} ''' at {self.created_at}"


class Notification(models.Model):
    SEND_BY_SYSTEM = 'ss'
    SEND_BY_ADMIN = 'sa'

    TYPES = (
        (SEND_BY_SYSTEM, 'ارسال شده توسط سامانه'),
        (SEND_BY_ADMIN, 'ارسال شده توسط ادمین')
    )

    type = models.CharField(max_length=2, choices=TYPES, default=SEND_BY_SYSTEM)

    send_datetime = models.DateTimeField(blank=True, null=True)
    notification_title = models.CharField(max_length=255, blank=True, null=True)
    notification_explanation = models.TextField(blank=True, null=True)
    notification_link = models.CharField(max_length=255, blank=True, null=True)
    is_sent = models.BooleanField(default=False)

    send_sms = models.BooleanField(default=False)
    sms_text = models.CharField(max_length=500, blank=True, null=True)

    receivers = models.ManyToManyField('users.User', related_name='user_in_notification')

    product = models.ForeignKey(
        'products.Product',
        related_name='offer_notifications',
        on_delete=models.CASCADE,
        db_index=True
    )

    def __str__(self):
        return "{} ({})".format(self.notification_title, self.id)

    def create_user_notifications(self):
        for receiver in self.receivers.all():
            self.userNotifications.create(
                user=receiver,
                status=UserNotification.NOT_READ,
            )
        self.is_sent = True
        self.save()


class UserNotification(models.Model):
    PENDING = 'p'
    SENT = 's'
    READ = 'r'
    NOT_READ = 'ur'

    STATUSES = (
        (PENDING, 'در انتظار ارسال'),
        (READ, 'خوانده شده'),
        (NOT_READ, 'خوانده نشده')
    )

    SMS_STATUSES = (
        (PENDING, 'در انتظار ارسال'),
        (SENT, 'ارسال شده'),
    )

    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name='crmUserNotifications')
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='crmNotifications')

    notification_status = models.CharField(choices=STATUSES, max_length=2, blank=True, null=True)
    sms_status = models.CharField(choices=STATUSES, max_length=2, blank=True, null=True)

    def __str__(self):
        return "{} -> {} ({})".format(self.notification, self.user, self.id)

    def send_sms(self):
        Sms.send(phone=self.user.mobile_number, message=self.notification.sms_text)
        self.sms_status = self.SENT
        self.save()



