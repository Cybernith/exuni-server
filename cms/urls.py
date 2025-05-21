from django.conf.urls import url

from cms.views import HeaderElementApiView, AllHeaderElementApiView, PopUpElementApiView, AllPopUpElementApiView, \
    BannerContentApiView, AllBannerContentApiView, HeaderElementDetailView, PopUpElementDetailView, \
    BannerContentDetailView, BannerContentItemApiView, BannerContentItemDetailView, ShopHomePageStoryApiView, \
    AllShopHomePageStoryApiView, ShopHomePageStoryDetailView, CurrentShopHomeHighlightApiView

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

    url(r'^currentShopHomeHighlight$', CurrentShopHomeHighlightApiView.as_view(), name='currentShopHomeHighlight'),

    url(r'^currentShopHomePageStory$', ShopHomePageStoryApiView.as_view(), name='currentShopHomePageStory'),
    url(r'^shopHomePageStory$', AllShopHomePageStoryApiView.as_view(), name='shopHomePageStory'),
    url(r'^shopHomePageStory/(?P<pk>[0-9]+)$', ShopHomePageStoryDetailView.as_view(), name='shopHomePageStoryDetail'),

]
