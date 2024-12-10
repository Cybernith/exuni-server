from django.conf.urls import url

from packing.lists.views import OrderPackageWithoutAdminListView
from packing.views import OrderPackageApiView, OrderPackageDetailView, AddAdminToOrdersApiView

app_name = 'packing'
urlpatterns = [
    url(r'^orderWithoutAdmin$', OrderPackageWithoutAdminListView.as_view(), name='orderPackageWithoutAdminListView'),
    url(r'^addAdminToOrders$', AddAdminToOrdersApiView.as_view(), name='addAdminToOrdersApiView'),
    url(r'^order$', OrderPackageApiView.as_view(), name='orderPackageApiView'),
    url(r'^order/(?P<pk>[0-9]+)$', OrderPackageDetailView.as_view(), name='orderPackageDetailView'),

]
