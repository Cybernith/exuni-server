import datetime
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

from helpers.models import BaseModel, DECIMAL
import random


def custom_upload_to(instance, filename):
    return 'images/{filename}'.format(filename=filename)


class HeaderElement(BaseModel):
    from_date_time = models.DateTimeField()
    to_date_time = models.DateTimeField()
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    mobile_image = models.ImageField(upload_to=custom_upload_to)
    desktop_image = models.ImageField(upload_to=custom_upload_to)
    link = models.URLField(max_length=100)

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


class PopUpElement(BaseModel):
    from_date_time = models.DateTimeField()
    to_date_time = models.DateTimeField()
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


class BannerContent(BaseModel):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5

    ORDERS = (
        (ONE, 'بنر اصلی'),
        (TWO, 'بنر دو'),
        (THREE, 'بنر سه'),
        (FOUR, 'بنر چهار'),
        (FIVE, 'بنر پنج'),
    )

    from_date_time = models.DateTimeField()
    to_date_time = models.DateTimeField()
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


class BannerContentItem(BaseModel):
    pop_up_element = models.ForeignKey(PopUpElement, related_name='items', on_delete=models.CASCADE)
    title = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    mobile_image = models.ImageField(upload_to=custom_upload_to)
    desktop_image = models.ImageField(upload_to=custom_upload_to)
    link = models.URLField(max_length=100)

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
