from django.conf.urls import url

from shop.views import CurrentUserCartApiView, CartDetailView, CurrentUserWishListApiView, WishListDetailView, \
    CurrentUserComparisonApiView, ComparisonDetailView, CurrentUserShipmentAddressApiView, ShipmentAddressDetailView, \
    CurrentLimitedTimeOfferRetrieveView, ProductRateApiView, ProductRateDetailView

app_name = 'shop'
urlpatterns = [
    url(r'^currentUserCart$', CurrentUserCartApiView.as_view(), name='currentUserCart'),
    url(r'^cart/(?P<pk>[0-9]+)$', CartDetailView.as_view(), name='cartDetail'),

    url(r'^currentUserWishList$', CurrentUserWishListApiView.as_view(), name='currentUserWishList'),
    url(r'^wishList/(?P<pk>[0-9]+)$', WishListDetailView.as_view(), name='wishListDetail'),

    url(r'^currentUserComparison$', CurrentUserComparisonApiView.as_view(), name='currentUserComparison'),
    url(r'^comparison/(?P<pk>[0-9]+)$', ComparisonDetailView.as_view(), name='comparisonDetail'),

    url(r'^currentUserShipmentAddress$', CurrentUserShipmentAddressApiView.as_view(),
        name='currentUserShipmentAddress'),
    url(r'^shipmentAddress/(?P<pk>[0-9]+)$', ShipmentAddressDetailView.as_view(), name='shipmentAddress'),

    url(r'^currentLimitedTimeOffer$', CurrentLimitedTimeOfferRetrieveView.as_view(), name='currentLimitedTimeOffer'),

    url(r'^rate$', ProductRateApiView.as_view(), name='productRate'),
    url(r'^rate/(?P<pk>[0-9]+)$', ProductRateDetailView.as_view(), name='productRateDetail'),

]
