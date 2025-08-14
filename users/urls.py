from django.conf.urls import url
from rest_framework.routers import DefaultRouter
from django.urls import path

from users.views.auth_views import SecretKeyView
from users.views.citiesView import CityListCreateView, CityDetailView
from users.views.notification_views import UserNotificationListView, ChangeUserNotificationStatusView, \
    SendNotificationModelView, ReminderNotificationModelView
from users.views.rolesView import RoleCreateView, RoleUpdateView, RoleDestroyView, RoleListView, PermissionListView
from users.views.usersView import CurrentUserApiView, UserCreateView, \
    UserUpdateView, UserListView, ChangePasswordView, SendVerificationCodeView, CheckVerificationCodeView, \
    ChangePasswordByVerificationCodeView, ChangePhoneView, \
    CheckVerificationForRegister, \
    CurrentUserNotificationApiView

router = DefaultRouter()
urlpatterns = router.urls + [
    url(r'^create$', UserCreateView.as_view(), name='create-user'),
    url(r'^update/(?P<pk>[0-9]+)$', UserUpdateView.as_view(), name='update-user'),
    url(r'^changePassword$', ChangePasswordView.as_view(), name='change-user-password'),
    url(r'^changePhone$', ChangePhoneView.as_view(), name='change-user-phone'),

    url(r'^list$', UserListView.as_view(), name='list-users'),

    url(r'^sendVerificationCode$', SendVerificationCodeView.as_view()),
    url(r'^checkVerificationCode$', CheckVerificationCodeView.as_view()),
    url(r'^checkVerificationForRegister$', CheckVerificationForRegister.as_view()),
    url(r'^changePasswordByVerificationCode$', ChangePasswordByVerificationCodeView.as_view()),
    url(r'^changePhoneByVerificationCode$', ChangePhoneView.as_view()),

    url(r'^roles/create$', RoleCreateView.as_view(), name='create-role'),
    url(r'^roles/update/(?P<pk>[0-9]+)$', RoleUpdateView.as_view(), name='update-role'),
    url(r'^roles/delete/(?P<pk>[0-9]+)$', RoleDestroyView.as_view(), name='destroy-role'),
    url(r'^roles/list$', RoleListView.as_view(), name='list-roles'),
    url(r'^permissions/list$', PermissionListView.as_view(), name='list-permissions'),

    url(r'^currentUser/$', CurrentUserApiView.as_view(), name='current-user'),


    url('secretKey', SecretKeyView.as_view(), name='update-secret-key'),

    url('notifications/changeStatus', ChangeUserNotificationStatusView.as_view(),
        name='change-user-notification-status'),
    url('notifications', UserNotificationListView.as_view(), name='user-notifications-list'),

]
