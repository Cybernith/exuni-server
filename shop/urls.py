from django.conf.urls import url

from products.shop.views import CommentCreateView, ShopProductCommentListView, RateUpsertApiView
from shop.search import GlobalAutoCompleteSearchAPIView
from shop.views import CurrentUserCartApiView, CartDetailView, CurrentUserWishListApiView, WishListDetailView, \
    CurrentUserComparisonApiView, ComparisonDetailView, CurrentUserShipmentAddressApiView, ShipmentAddressDetailView, \
    CurrentLimitedTimeOfferRetrieveView, ProductRateApiView, ProductRateDetailView, PostCommentApiView, \
    CommentDetailView, ShopOrderStatusHistoryApiView, StartPaymentApiView, PaymentCallbackApiView, \
    StartZarinpalPaymentApiView, ZarinpalCallbackApiView, UserProductRateApiView, CartSyncView, WishlistSyncView, \
    ComparisonSyncView, SyncAllDataView, ShopOrderRegistrationView, CustomerOrdersDetailView, ClearCustomerCartView

app_name = 'shop'
urlpatterns = [
    url(r'^searchAutoCompelete$', GlobalAutoCompleteSearchAPIView.as_view(), name='globalAutoCompleteSearch'),

    url(r'^currentUserCart$', CurrentUserCartApiView.as_view(), name='currentUserCart'),
    url(r'^cartSync$', CartSyncView.as_view(), name='cartSync'),
    url(r'^cart/(?P<pk>[0-9]+)$', CartDetailView.as_view(), name='cartDetail'),
    url(r'^clearCard/(?P<pk>[0-9]+)$', ClearCustomerCartView.as_view(), name='clearCustomerCart'),

    url(r'^currentUserWishList$', CurrentUserWishListApiView.as_view(), name='currentUserWishList'),
    url(r'^wishlistSync$', WishlistSyncView.as_view(), name='wishlistSync'),
    url(r'^wishList/(?P<pk>[0-9]+)$', WishListDetailView.as_view(), name='wishListDetail'),

    url(r'^currentUserComparison$', CurrentUserComparisonApiView.as_view(), name='currentUserComparison'),
    url(r'^comparisonSync$', ComparisonSyncView.as_view(), name='comparisonSync'),
    url(r'^comparison/(?P<pk>[0-9]+)$', ComparisonDetailView.as_view(), name='comparisonDetail'),

    url(r'^syncUserAllData$', SyncAllDataView.as_view(), name='syncUserAllData'),

    url(r'^currentUserShipmentAddress$', CurrentUserShipmentAddressApiView.as_view(),
        name='currentUserShipmentAddress'),
    url(r'^shipmentAddress/(?P<pk>[0-9]+)$', ShipmentAddressDetailView.as_view(), name='shipmentAddress'),

    url(r'^currentLimitedTimeOffer$', CurrentLimitedTimeOfferRetrieveView.as_view(), name='currentLimitedTimeOffer'),

    url(r'^rate$', ProductRateApiView.as_view(), name='productRate'),
    url(r'^rate/(?P<pk>[0-9]+)$', ProductRateDetailView.as_view(), name='productRateDetail'),

    #url(r'^postComment$', PostCommentApiView.as_view(), name='postComment'),

    url(r'^comment/(?P<pk>[0-9]+)$', CommentDetailView.as_view(), name='commentDetail'),

    url(r'^orderStatusHistory/(?P<order_id>[0-9]+)$', ShopOrderStatusHistoryApiView.as_view(),
        name='shopOrderStatusHistory'),

    url(r'^paymentStart/(?P<order_id>[0-9]+)$', StartPaymentApiView.as_view(), name='startPayment'),
    url(r'^paymentCallback$', PaymentCallbackApiView.as_view(), name='paymentCallback'),

    url(r'^zarinpalPaymentStart/(?P<order_id>[0-9]+)$', StartZarinpalPaymentApiView.as_view(), name='zarinpal_start'),
    url(r'^zarinpalPaymentCallback$', ZarinpalCallbackApiView.as_view(), name='zarinpal_callback'),

    url(r'^sendComment$', CommentCreateView.as_view(), name='sendComment'),
    url(r'^sendRate$', RateUpsertApiView.as_view(), name='sendRate'),
    url(r'^product/(?P<id>[0-9]+)/comments$', ShopProductCommentListView.as_view(), name='shopProductComments'),
    url(r'^product/(?P<product_id>[0-9]+)/userRate$', UserProductRateApiView.as_view(), name='productUserRate'),

    url(r'^createOrder$', ShopOrderRegistrationView.as_view(), name='createOrder'),
    url(r'^customerOrders/(?P<pk>[0-9]+)$', CustomerOrdersDetailView.as_view(), name='customerOrders'),
]
