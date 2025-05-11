from django.conf.urls import url

from products.shop.views import ShopProductSimpleListView, BrandShopListView, CategoryTreeView, RootCategoryListView

urlpatterns = [
    url(r'^products$', ShopProductSimpleListView.as_view(), name='shopProductSimpleList'),
    url(r'^brands$', BrandShopListView.as_view(),name='brandShop'),
    url(r'^categoryTree$', CategoryTreeView.as_view(), name='categoryTree'),
    url(r'^rootCategories$', RootCategoryListView.as_view(), name='rootCategories'),

]
