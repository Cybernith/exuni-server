from django.conf.urls import url

from cms.views import HeaderElementApiView, AllHeaderElementApiView, PopUpElementApiView, AllPopUpElementApiView, \
    BannerContentApiView, AllBannerContentApiView, HeaderElementDetailView, PopUpElementDetailView, \
    BannerContentDetailView, BannerContentItemApiView, BannerContentItemDetailView

app_name = 'cms'
urlpatterns = [
    url(r'^currentHeaderElement$', HeaderElementApiView.as_view(), name='currentHeaderElement'),
    url(r'^headerElement$', AllHeaderElementApiView.as_view(), name='headerElement'),
    url(r'^headerElement/(?P<pk>[0-9]+)$', HeaderElementDetailView.as_view(), name='headerElementDetail'),

    url(r'^currentPopUpElement$', PopUpElementApiView.as_view(), name='currentPopUpElement'),
    url(r'^popUpElement$', AllPopUpElementApiView.as_view(), name='popUpElement'),
    url(r'^popUpElement/(?P<pk>[0-9]+)$', PopUpElementDetailView.as_view(), name='popUpElementDetail'),

    url(r'^currentBannerContent$', BannerContentApiView.as_view(), name='currentBannerContent'),
    url(r'^bannerContent$', AllBannerContentApiView.as_view(), name='bannerContent'),
    url(r'^bannerContent/(?P<pk>[0-9]+)$', BannerContentDetailView.as_view(), name='bannerContentDetail'),

    url(r'^bannerContentItem$', BannerContentItemApiView.as_view(), name='bannerContentItem'),
    url(r'^bannerContentItem/(?P<pk>[0-9]+)$', BannerContentItemDetailView.as_view(), name='bannerContentItemDetail'),

]
