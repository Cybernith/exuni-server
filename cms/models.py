from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

from cms.managers import CMSCustomManager
from helpers.functions import datetime_to_str
from helpers.models import BaseModel


def custom_upload_to(instance, filename):
    return 'images/{filename}'.format(filename=filename)


class DateTimeRangeModel(models.Model):
    from_date_time = models.DateTimeField(blank=True, null=True)
    to_date_time = models.DateTimeField(blank=True, null=True)
    objects = CMSCustomManager()

    class Meta:
        abstract = True


class HeaderElement(BaseModel, DateTimeRangeModel):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    mobile_image = models.ImageField(upload_to=custom_upload_to)
    desktop_image = models.ImageField(upload_to=custom_upload_to)
    link = models.URLField(max_length=100)
    discount_code = models.ForeignKey(
        'subscription.DiscountCode',
        related_name='header_elements',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    objects = CMSCustomManager()


    class Meta(BaseModel.Meta):
        verbose_name = 'HeaderElement'
        permission_basename = 'header_element'
        permissions = (
            ('get.header_element', 'مشاهده عنصر هدر'),
            ('create.header_element', 'تعریف عنصر هدر'),
            ('update.header_element', 'ویرایش عنصر هدر'),
            ('delete.header_element', 'حذف عنصر هدر'),

            ('getOwn.header_element', 'مشاهده عنصر هدر خود'),
            ('updateOwn.header_element', 'ویرایش عنصر هدر خود'),
            ('deleteOwn.header_element', 'حذف عنصر هدر خود'),
        )

    def __str__(self):
        return "{} از {} تا {}".format(
            self.title, datetime_to_str(self.from_date_time), datetime_to_str(self.to_date_time)
        )


class PopUpElement(BaseModel, DateTimeRangeModel):
    title = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    has_button = models.BooleanField(default=False)
    button_title = models.CharField(max_length=100, blank=True, null=True)
    mobile_image = models.ImageField(upload_to=custom_upload_to)
    desktop_image = models.ImageField(upload_to=custom_upload_to)
    has_default_picture = models.BooleanField(default=False)
    display_seconds = models.IntegerField(
        default=3,
        validators=[MaxValueValidator(60), MinValueValidator(1)]
    )
    link = models.URLField(max_length=100)
    discount_code = models.ForeignKey(
        'subscription.DiscountCode',
        related_name='pop_up_elements',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    objects = CMSCustomManager()

    class Meta(BaseModel.Meta):
        verbose_name = 'PopUpElement'
        permission_basename = 'pop_up_element'
        permissions = (
            ('get.pop_up_element', 'مشاهده عنصر پاپ آپ'),
            ('create.pop_up_element', 'تعریف عنصر پاپ آپ'),
            ('update.pop_up_element', 'ویرایش عنصر پاپ آپ'),
            ('delete.pop_up_element', 'حذف عنصر پاپ آپ'),

            ('getOwn.pop_up_element', 'مشاهده عنصر پاپ آپ خود'),
            ('updateOwn.pop_up_element', 'ویرایش عنصر پاپ آپ خود'),
            ('deleteOwn.pop_up_element', 'حذف عنصر پاپ آپ خود'),
        )

    def __str__(self):
        return "{} از {} تا {}".format(
            self.title, datetime_to_str(self.from_date_time), datetime_to_str(self.to_date_time)
        )


class BannerContent(BaseModel, DateTimeRangeModel):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6

    ORDERS = (
        (ONE, 'بنر اصلی'),
        (TWO, 'بنر دو'),
        (THREE, 'بنر سه'),
        (FOUR, 'بنر چهار'),
        (FIVE, 'بنر پنج'),
        (SIX, 'بنر شش'),
    )

    title = models.CharField(max_length=100, blank=True, null=True)
    auto_scroll_seconds = models.IntegerField(
        default=5,
        validators=[MaxValueValidator(60), MinValueValidator(1)]
    )
    order = models.IntegerField(choices=ORDERS, default=ONE)

    class Meta(BaseModel.Meta):
        verbose_name = 'BannerContent'
        permission_basename = 'banner_content'
        permissions = (
            ('get.banner_content', 'مشاهده محتوا بنر'),
            ('create.banner_content', 'تعریف محتوا بنر'),
            ('update.banner_content', 'ویرایش محتوا بنر'),
            ('delete.banner_content', 'حذف محتوا بنر'),

            ('getOwn.banner_content', 'مشاهده محتوا بنر خود'),
            ('updateOwn.banner_content', 'ویرایش محتوا بنر خود'),
            ('deleteOwn.banner_content', 'حذف محتوا بنر خود'),
        )
    objects = CMSCustomManager()

    def __str__(self):
        title = self.title if self.title else ' '
        return "{} از {} تا {}".format(
            title, datetime_to_str(self.from_date_time), datetime_to_str(self.to_date_time)
        )


class BannerContentItem(BaseModel):
    banner_content = models.ForeignKey(BannerContent, related_name='items',
                                       on_delete=models.CASCADE, blank=True, null=True)
    title = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    mobile_image = models.ImageField(upload_to=custom_upload_to)
    desktop_image = models.ImageField(upload_to=custom_upload_to)
    link = models.URLField(max_length=100)
    discount_code = models.ForeignKey(
        'subscription.DiscountCode',
        related_name='banner_content_item',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )

    class Meta(BaseModel.Meta):
        verbose_name = 'BannerContentItem'
        permission_basename = 'banner_content_item'
        permissions = (
            ('get.banner_content_item', 'مشاهده آیتم محتوا بنر'),
            ('create.banner_content_item', 'تعریف آیتم محتوا بنر'),
            ('update.banner_content_item', 'ویرایش آیتم محتوا بنر'),
            ('delete.banner_content_item', 'حذف آیتم محتوا بنر'),

            ('getOwn.banner_content_item', 'مشاهده آیتم محتوا بنر خود'),
            ('updateOwn.banner_content_item', 'ویرایش آیتم محتوا بنر خود'),
            ('deleteOwn.banner_content_item', 'حذف آیتم محتوا بنر خود'),
        )


class ShopHomePageStory(BaseModel, DateTimeRangeModel):
    title = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    mobile_image = models.ImageField(upload_to=custom_upload_to)
    desktop_image = models.ImageField(upload_to=custom_upload_to)
    video = models.FileField(upload_to=custom_upload_to, blank=True, null=True)
    link = models.URLField(max_length=100, blank=True, null=True)
    discount_code = models.ForeignKey(
        'subscription.DiscountCode',
        related_name='shop_home_stories',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    objects = CMSCustomManager()

    class Meta(BaseModel.Meta):
        verbose_name = 'ShopHomePageStory'
        permission_basename = 'shop_home_page_story'
        permissions = (
            ('get.shop_home_page_story', 'مشاهده استوری'),
            ('create.shop_home_page_story', 'تعریف استوری'),
            ('update.shop_home_page_story', 'ویرایش استوری'),
            ('delete.shop_home_page_story', 'حذف استوری'),

            ('getOwn.shop_home_page_story', 'مشاهده استوری خود'),
            ('updateOwn.shop_home_page_story', 'ویرایش استوری خود'),
            ('deleteOwn.shop_home_page_story', 'حذف استوری خود'),
        )
