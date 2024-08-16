from django.db import models

from helpers.functions import get_current_user
from helpers.models import BaseModel


class Option(BaseModel):
    name = models.CharField(max_length=255)
    codename = models.CharField(max_length=255, unique=True)
    usage = models.CharField(max_length=100, blank=True, null=True)
    value = models.TextField(blank=True, null=True)

    class Meta(BaseModel.Meta):
        permission_basename = 'option'
        permissions = (
            ('get.option', 'مشاهده تنظیمات'),
            ('update.option', 'ویرایش تنظیمات'),
        )

    @staticmethod
    def get_option(codename):
        codename = str(codename)
        try:
            option = Option.objects.get(codename=codename)
        except Option.DoesNotExist:
            option = Option.objects.create(codename=codename)
        return option

    @staticmethod
    def get_value(codename, default=None):
        value = Option.get_option(codename).value
        return value if value else default

    @staticmethod
    def set_value(codename, value):
        option = Option.get_option(codename)
        option.value = str(value)
        option.save()

    @staticmethod
    def get_order_id():
        last_order_id = Option.get_value('order_id')
        last_order_id = int(last_order_id) if last_order_id else 0
        last_order_id += 1
        Option.set_value('order_id', last_order_id)
        return last_order_id


