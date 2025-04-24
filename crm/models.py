from django.db import models

from helpers.models import TimeStampedModel

from user_agents import parse as user_agent_parse


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

    @property
    def user_agent_object(self):
        return user_agent_parse(self.user_agent or '')

    @property
    def browser_type(self):
        return self.user_agent_object.browser.family

    @property
    def browser_version(self):
        version = self.user_agent_object.browser.version
        return '.'.join(str(version_value) for version_value in version) if version else None

    @property
    def os_type(self):
        return self.user_agent_object.os.family

    @property
    def os_version(self):
        version = self.user_agent_object.os.version
        return '.'.join(str(version_value) for version_value in version) if version else None

    @property
    def device_family(self):
        return self.user_agent_object.device.version or None

    @property
    def user_device(self):
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
    def is_touch_device(self):
        return self.user_agent_object.is_touch_capable

    class Meta:
        abstract = True


class ShopProductViewLog(TimeStampedModel, UserAgentModel):
    product = models.ForeignKey(
        'products.Product',
        related_name='views_log',
        on_delete=models.CASCADE,
        db_index=True
    )
    user = models.ForeignKey(
        'users.User',
        related_name='product_views',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    ip_address = models.CharField(max_length=45)
    referer = models.URLField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product', 'created_at']),
            models.Index(fields=['user', 'created_at'])
        ]

    def __str__(self):
        return f"view of product {self.product.name} by {self.user.name or 'guest'} at {self.created_at}"

    def save(self, *args, **kwargs):
        if not self.id and not self.device_type:
            self.device_type = self.user_device

        super().save(*args, **kwargs)




