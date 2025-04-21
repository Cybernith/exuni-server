from django.contrib import admin

from cms.models import HeaderElement, PopUpElement, BannerContent, BannerContentItem

admin.site.register(HeaderElement)
admin.site.register(PopUpElement)
admin.site.register(BannerContent)
admin.site.register(BannerContentItem)
