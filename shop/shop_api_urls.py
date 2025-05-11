from django.conf.urls import url

from cms.views import HeaderElementApiView, PopUpElementApiView, BannerContentApiView, ShopHomePageStoryApiView
from products.shop.views import ShopProductSimpleListView, BrandShopListView, CategoryTreeView, RootCategoryListView, \
    ShopProductWithCommentsListView
from shop.search import GlobalAutoCompleteSearchAPIView
from shop.views import ToggleWishListBTNView, ToggleComparisonListBTNView, CurrentUserCartApiView, CartSyncView, \
    CartDetailView, ClearCustomerCartView, CurrentUserWishListApiView, WishListDetailView, WishlistSyncView, \
    CurrentUserComparisonApiView, ComparisonSyncView, ComparisonDetailView, SyncAllDataView, \
    ClearCustomerComparisonView, ClearCustomerWishListView, CurrentUserShipmentAddressApiView, ShipmentAddressDetailView

urlpatterns = [
    # limit - offset - ordering - topRated -> boolean - top viewd -> booleand
    url(r'^products$', ShopProductSimpleListView.as_view(), name='shopProductSimpleList'),

    url(r'^brands$', BrandShopListView.as_view(),name='brandShop'),
    url(r'^categoryTree$', CategoryTreeView.as_view(), name='categoryTree'),
    url(r'^rootCategories$', RootCategoryListView.as_view(), name='rootCategories'),


    url(r'^toggleWishListBtn$', ToggleWishListBTNView.as_view(), name='toggleWishListBtn'),
    url(r'^toggleComparisonBtn$', ToggleComparisonListBTNView.as_view(), name='toggleComparisonBtn'),

    url(r'^currentUserCart$', CurrentUserCartApiView.as_view(), name='currentUserCart'),
    url(r'^cartSync$', CartSyncView.as_view(), name='cartSync'),
    url(r'^cart/(?P<pk>[0-9]+)$', CartDetailView.as_view(), name='cartDetail'),
    url(r'^clearCard$', ClearCustomerCartView.as_view(), name='clearCustomerCart'),

    url(r'^currentUserWishList$', CurrentUserWishListApiView.as_view(), name='currentUserWishList'),
    url(r'^wishlistSync$', WishlistSyncView.as_view(), name='wishlistSync'),
    url(r'^clearWishList$', ClearCustomerWishListView.as_view(), name='clearCustomerWishList'),

    url(r'^currentUserComparison$', CurrentUserComparisonApiView.as_view(), name='currentUserComparison'),
    url(r'^comparisonSync$', ComparisonSyncView.as_view(), name='comparisonSync'),
    url(r'^clearComparison$', ClearCustomerComparisonView.as_view(), name='clearCustomerComparison'),

    url(r'^syncUserAllData$', SyncAllDataView.as_view(), name='syncUserAllData'),

    url(r'^currentUserShipmentAddress$', CurrentUserShipmentAddressApiView.as_view(), name='syncUserAllData'),
    url(r'^shipmentAddress/(?P<pk>[0-9]+)$', ShipmentAddressDetailView.as_view(), name='shipmentAddress'),


    # content management system
    url(r'^currentHeaderElement$', HeaderElementApiView.as_view(), name='currentHeaderElement'),
    url(r'^currentPopUpElement$', PopUpElementApiView.as_view(), name='currentPopUpElement'),
    url(r'^currentBannerContent$', BannerContentApiView.as_view(), name='currentBannerContent'),
    url(r'^currentShopHomePageStory$', ShopHomePageStoryApiView.as_view(), name='currentShopHomePageStory'),

    url(r'^searchAutoCompelete$', GlobalAutoCompleteSearchAPIView.as_view(), name='globalAutoCompleteSearch'),

    url(r'^productsWithComments$', ShopProductWithCommentsListView.as_view(), name='productsWithComments'),

]
