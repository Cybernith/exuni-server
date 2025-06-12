from django.conf.urls import url

from cms.views import HeaderElementApiView, PopUpElementApiView, BannerContentApiView, ShopHomePageStoryApiView, \
    CurrentShopHomeHighlightApiView
from crm.views import UserCurrentNotificationsAPIView, UserCurrentNotificationsBySortAPIView, \
    RecommendedProductsAPIView, MarkNotificationAsReadView, InventoryReminderCreateView
from products.shop.views import ShopProductSimpleListView, BrandShopListView, CategoryTreeView, RootCategoryListView, \
    ShopProductWithCommentsListView, CurrentUserHasOrderProductViewSet, CurrentUserRelatedProductViewSet, \
    PendingReviewProductsView, UserProductsWithCommentView, CommentCreateView, RateUpsertApiView, \
    RelatedProductsApiView, SimilarBrandProductsApiView, ShopProductDetailView, ImageSearchAPIView
from products.views import AvailSubtreeView, AvailTreeSaveView, AvailRootListView, AvailDeleteView, FeatureSubtreeView, \
    FeatureDeleteView, FeatureTreeSaveView, FeatureRootListView, CategorizationSubtreeView, CategorizationDeleteView, \
    CategorizationTreeSaveView, CategorizationRootListView
from shop.search import GlobalAutoCompleteSearchAPIView
from shop.views import ToggleWishListBTNView, ToggleComparisonListBTNView, CurrentUserCartApiView, CartSyncView, \
    CartDetailView, ClearCustomerCartView, CurrentUserWishListApiView, WishlistSyncView, \
    CurrentUserComparisonApiView, ComparisonSyncView, SyncAllDataView, \
    ClearCustomerComparisonView, ClearCustomerWishListView, CurrentUserShipmentAddressApiView, \
    ShipmentAddressDetailView, UserOrdersListView, AddToCartAPIView, ShopOrderRegistrationView, \
    CustomerOrdersDetailView, ShopOrderStatusHistoryApiView, CustomerOrdersView, CustomerOrdersSearchView, \
    CancelShopOrderView, OrderMoveToCartAPIView
from users.views.usersView import CheckVerificationAndLogin, SendVerificationCodeView, UserUpdateView, ChangePhoneView, \
    CurrentUserApiView

urlpatterns = [
    # limit - offset - ordering - topRated -> boolean - top viewd -> booleand
    url(r'^login$', CheckVerificationAndLogin.as_view(), name='checkVerificationAndLogin'),
    url(r'^sendVerificationCode$', SendVerificationCodeView.as_view()),
    url(r'^userUpdate/(?P<pk>[0-9]+)$', UserUpdateView.as_view(), name='update-user'),
    url(r'^changePhoneByVerificationCode$', ChangePhoneView.as_view()),
    url(r'^currentUser/$', CurrentUserApiView.as_view(), name='current-user'),

    url(r'^products$', ShopProductSimpleListView.as_view(), name='shopProductSimpleList'),
    url(r'^productDetail/(?P<id>[0-9]+)$', ShopProductDetailView.as_view(), name='ProductDetail'),

    url(r'^brands$', BrandShopListView.as_view(),name='brandShop'),
    url(r'^categoryTree$', CategoryTreeView.as_view(), name='categoryTree'),
    url(r'^rootCategories$', RootCategoryListView.as_view(), name='rootCategories'),


    url(r'^toggleWishListBtn$', ToggleWishListBTNView.as_view(), name='toggleWishListBtn'),
    url(r'^toggleComparisonBtn$', ToggleComparisonListBTNView.as_view(), name='toggleComparisonBtn'),

    url(r'^currentUserCart$', CurrentUserCartApiView.as_view(), name='currentUserCart'),
    url(r'^cartAdd$', AddToCartAPIView.as_view(), name='addToCart'),
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
    url(r'^currentShopHomeHighlight$', CurrentShopHomeHighlightApiView.as_view(), name='currentShopHomeHighlight'),

    url(r'^searchAutoCompelete$', GlobalAutoCompleteSearchAPIView.as_view(), name='globalAutoCompleteSearch'),
    url(r'^imageSearch$', ImageSearchAPIView.as_view(), name='imageSearch'),

    url(r'^productsWithComments$', ShopProductWithCommentsListView.as_view(), name='productsWithComments'),

    url(r'^currentUserOrders$', UserOrdersListView.as_view(), name='userOrders'),

    url(r'^currentUserHasOrderProducts$', CurrentUserHasOrderProductViewSet.as_view({'get': 'list'}),
        name='currentUserHasOrderProducts'),

    url(r'^currentUserRelatedProduct$', CurrentUserRelatedProductViewSet.as_view({'get': 'list'}),
        name='currentUserRelatedProduct'),

    url(r'^pendingReviewProducts$', PendingReviewProductsView.as_view({'get': 'list'}),
        name='pendingReviewProducts'),

    url(r'^userProductsWithComment$', UserProductsWithCommentView.as_view({'get': 'list'}),
        name='userProductsWithComment'),

    url(r'^retrieveNotification$', UserCurrentNotificationsAPIView.as_view(),
        name='retrieveNotification'),

    url(r'^retrieveNotificationBySort$', UserCurrentNotificationsBySortAPIView.as_view(),
        name='retrieveNotificationBySort'),
    url(r'^inventoryReminder/(?P<product_id>[0-9]+)$', InventoryReminderCreateView.as_view(),
        name='inventoryReminder'),
    url(r'^markNotificationAsRead/(?P<notification_id>[0-9]+)$', MarkNotificationAsReadView.as_view(),
        name='markNotificationAsRead'),

    url(r'^sendComment$', CommentCreateView.as_view(), name='sendComment'),
    url(r'^sendRate$', RateUpsertApiView.as_view(), name='sendRate'),

    url(r'^product/(?P<product_id>[0-9]+)/related$', RelatedProductsApiView.as_view(), name='relatedProducts'),
    url(r'^product/(?P<product_id>[0-9]+)/similarBrand$', SimilarBrandProductsApiView.as_view(),
        name='similarBrandProducts'),
    url(r'^userRecommendation$', CurrentUserRelatedProductViewSet.as_view({'get': 'list'}),
        name='userRecommendation'),

    url(r'^createOrder$', ShopOrderRegistrationView.as_view(), name='createOrder'),
    url(r'^customerOrders', CustomerOrdersView.as_view(), name='customerOrders'),
    url(r'^customerOrderByCode$', CustomerOrdersSearchView.as_view(), name='customerOrderByCode$'),
    url(r'^orderStatusHistory/(?P<order_id>[0-9]+)$', ShopOrderStatusHistoryApiView.as_view(),
        name='shopOrderStatusHistory'),
    url(r'^customerOrderDetail/(?P<order_id>[0-9]+)$', CustomerOrdersDetailView.as_view(), name='customerOrdersDetail'),
    url(r'^cancelCustomerOrder/(?P<pk>[0-9]+)$', CancelShopOrderView.as_view(), name='cancelCustomerOrder'),
    url(r'^editCustomerOrder/(?P<pk>[0-9]+)$', OrderMoveToCartAPIView.as_view(), name='orderMoveToCart'),

    url(r'^availSubtree/(?P<pk>[0-9]+)$', AvailSubtreeView.as_view(), name='availSubtree'),
    url(r'^availDelete/(?P<pk>[0-9]+)$', AvailDeleteView.as_view(), name='availDeleteView'),
    url(r'^availSubtree$', AvailTreeSaveView.as_view(), name='availsTreeSave'),
    url(r'^availRootList$', AvailRootListView.as_view(), name='availRootList'),

    url(r'^featureSubtree/(?P<pk>[0-9]+)$', FeatureSubtreeView.as_view(), name='featureSubtree'),
    url(r'^featureDelete/(?P<pk>[0-9]+)$', FeatureDeleteView.as_view(), name='featureDeleteView'),
    url(r'^featureSubtree$', FeatureTreeSaveView.as_view(), name='featureTreeSave'),
    url(r'^featureRootList$', FeatureRootListView.as_view(), name='featureRootList'),

    url(r'^categorizationSubtree/(?P<pk>[0-9]+)$', CategorizationSubtreeView.as_view(), name='categorizationSubtree'),
    url(r'^categorizationDelete/(?P<pk>[0-9]+)$', CategorizationDeleteView.as_view(), name='categorizationDelete'),
    url(r'^categorizationSubtree$', CategorizationTreeSaveView.as_view(), name='categorizationSubtree'),
    url(r'^categorizationRootList$', CategorizationRootListView.as_view(), name='categorizationRootList'),
]
