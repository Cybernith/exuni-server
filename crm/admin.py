from django.contrib import admin

from crm.models import ShopProductViewLog, SearchLog, Notification, UserNotification

admin.site.register(ShopProductViewLog)
admin.site.register(SearchLog)
admin.site.register(Notification)
admin.site.register(UserNotification)
