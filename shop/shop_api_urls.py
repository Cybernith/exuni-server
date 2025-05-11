from django.conf.urls import url

from products.shop.views import ShopProductSimpleListView, BrandShopListView, CategoryTreeView, RootCategoryListView
from shop.views import ToggleWishListBTNView, ToggleComparisonListBTNView

urlpatterns = [
    # limit - offset - ordering - topRated -> boolean - top viewd -> booleand
    url(r'^products$', ShopProductSimpleListView.as_view(), name='shopProductSimpleList'),

    url(r'^brands$', BrandShopListView.as_view(),name='brandShop'),
    url(r'^categoryTree$', CategoryTreeView.as_view(), name='categoryTree'),
    url(r'^rootCategories$', RootCategoryListView.as_view(), name='rootCategories'),


    url(r'^toggleWishListBtn$', ToggleWishListBTNView.as_view(), name='toggleWishListBtn'),
    url(r'^toggleComparisonBtn$', ToggleComparisonListBTNView.as_view(), name='toggleComparisonBtn'),

]
