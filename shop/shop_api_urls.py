from django.conf.urls import url

from products.shop.views import ShopProductSimpleListView, BrandShopListView

urlpatterns = [
    url(r'^products$', ShopProductSimpleListView.as_view(), name='shopProductSimpleList'),
    url(r'^brands$', BrandShopListView.as_view(),name='brandShop'),

]
