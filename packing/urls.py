from django.conf.urls import url

from packing.lists.views import OrderPackageWithoutAdminListView, WaitingForPackingOrdersListView, \
    WaitingForShippingOrdersListView, AdminPackingReportListView
from packing.views import OrderPackageApiView, OrderPackageDetailView, AddAdminToOrdersApiView, \
    PackedOrderPackagesApiView, ShippingOrderPackagesApiView

app_name = 'packing'
urlpatterns = [
    url(r'^orderWithoutAdmin$', OrderPackageWithoutAdminListView.as_view(), name='orderPackageWithoutAdminListView'),
    url(r'^waitingForPackingOrders$', WaitingForPackingOrdersListView.as_view(), name='waitingForPackingOrdersListView'),
    url(r'^waitingForShippingOrders$', WaitingForShippingOrdersListView.as_view(), name='waitingForShippingOrdersListView'),
    url(r'^adminPackingReport$', AdminPackingReportListView.as_view(), name='adminPackingReportListView'),
    url(r'^addAdminToOrders$', AddAdminToOrdersApiView.as_view(), name='addAdminToOrdersApiView'),
    url(r'^packedOrderPackages$', PackedOrderPackagesApiView.as_view(), name='packedOrderPackagesApiView'),
    url(r'^shippedOrderPackages$', ShippingOrderPackagesApiView.as_view(), name='shippingOrderPackagesApiView'),
    url(r'^order$', OrderPackageApiView.as_view(), name='orderPackageApiView'),
    url(r'^order/(?P<pk>[0-9]+)$', OrderPackageDetailView.as_view(), name='orderPackageDetailView'),

]
