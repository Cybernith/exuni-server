from django.conf.urls import url

from shop.views import CurrentUserCartApiView, CartDetailView, CurrentUserWishListApiView, WishListDetailView, \
    CurrentUserComparisonApiView, ComparisonDetailView

app_name = 'shop'
urlpatterns = [
    url(r'^currentUserCart$', CurrentUserCartApiView.as_view(), name='currentUserCart'),
    url(r'^cart/(?P<pk>[0-9]+)$', CartDetailView.as_view(), name='cartDetail'),

    url(r'^currentUserWishList$', CurrentUserWishListApiView.as_view(), name='currentUserWishList'),
    url(r'^wishList/(?P<pk>[0-9]+)$', WishListDetailView.as_view(), name='wishListDetail'),

    url(r'^currentUserComparison$', CurrentUserComparisonApiView.as_view(), name='currentUserComparison'),
    url(r'^comparison/(?P<pk>[0-9]+)$', ComparisonDetailView.as_view(), name='comparisonDetail'),

]
