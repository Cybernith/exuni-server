from django.conf.urls import url

from cms.views import HeaderElementApiView, AllHeaderElementApiView, PopUpElementApiView, AllPopUpElementApiView, \
    BannerContentApiView, AllBannerContentApiView

app_name = 'products'
urlpatterns = [
    url(r'^currentHeaderElement$', HeaderElementApiView.as_view(), name='currentHeaderElement'),
    url(r'^headerElement$', AllHeaderElementApiView.as_view(), name='headerElement'),

    url(r'^currentPopUpElement$', PopUpElementApiView.as_view(), name='currentPopUpElement'),
    url(r'^popUpElement$', AllPopUpElementApiView.as_view(), name='popUpElement'),

    url(r'^currentBannerContent$', BannerContentApiView.as_view(), name='currentBannerContent'),
    url(r'^bannerContent$', AllBannerContentApiView.as_view(), name='bannerContent'),

]
