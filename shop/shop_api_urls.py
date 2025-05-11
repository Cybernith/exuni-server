from django.conf.urls import url

from products.shop.views import ShopProductSimpleListView

urlpatterns = [
    url(r'^products$', ShopProductSimpleListView.as_view(), name='shopProductSimpleList'),
]
