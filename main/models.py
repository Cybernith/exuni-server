from django.db import models
from django.db.models import Q
from django_jalali.db import models as jmodels

from helpers.models import BaseModel
from users.models import custom_upload_to


class BUSINESS(BaseModel):
    ONLINE_MARKET = 'om'
    COMMISSION_SELLER = 'cs'
    REPRESENTATION_MARKET = 'rm'

    BUSINESS_TYPES = (
        (ONLINE_MARKET, 'فروشگاه اینترنتی '),
        (COMMISSION_SELLER, 'فروشنده پورسانتی'),
        (REPRESENTATION_MARKET, 'فروشگاه نمایندگی'),
    )

    name = models.CharField(max_length=150)
    domain_address = models.CharField(max_length=150, blank=True, null=True)
    logo = models.ImageField(upload_to=custom_upload_to, null=True, blank=True, default=None)
    api_token = models.CharField(max_length=150, blank=True, null=True)
    primary_business_color = models.CharField(max_length=7, blank=True, null=True)
    secondary_business_color = models.CharField(max_length=7, blank=True, null=True)
    theme_business_color = models.CharField(max_length=7, blank=True, null=True)
    business_owner_national_card_picture = models.ImageField(upload_to=custom_upload_to,
                                                             null=True, blank=True, default=None)
    about_us = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    business_type = models.CharField(max_length=2, choices=BUSINESS_TYPES, default=ONLINE_MARKET)


    class Meta(BaseModel.Meta):
        verbose_name = 'Business'
        permission_basename = 'business'
        permissions = (
            ('get.business', 'مشاهده کسب و کار'),
            ('create.business', 'تعریف کسب و کار'),
            ('update.business', 'ویرایش کسب و کار'),
            ('delete.business', 'حذف کسب و کار'),

            ('getOwn.business', 'مشاهده کسب و کار خود'),
            ('updateOwn.business', 'ویرایش کسب و کار خود'),
            ('deleteOwn.business', 'حذف کسب و کار خود'),
        )
