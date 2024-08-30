from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Permission

from users.models import User, Role, PhoneVerification, Notification, UserNotification, City

UserAdmin.fieldsets += (('Secrets', {'fields': ('secret_key',)}),)
UserAdmin.fieldsets += (('نوع کاربر', {'fields': ('user_type',)}),)
UserAdmin.fieldsets += (('اطلاعات کاربر', {'fields': (
    'mobile_number',
    'national_code',
    'profile_picture',
    'cover_picture',
    'city',
    'address',
    'about_us',
)}),)
UserAdmin.fieldsets += (('اطلاعات بانکی', {'fields': (
    'bank_account_name',
    'bank_account_number',
    'bank_card_number',
    'bank_sheba_number',
)}),)


class PermissionAdmin(admin.ModelAdmin):
    search_fields = ('id', 'name', 'codename')


admin.site.register(User, UserAdmin)
admin.site.register(Role)
admin.site.register(Permission, PermissionAdmin)
admin.site.register(PhoneVerification)
admin.site.register(Notification)
admin.site.register(UserNotification)
admin.site.register(City)
