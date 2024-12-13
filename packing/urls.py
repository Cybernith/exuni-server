from django.conf.urls import url

from packing.lists.export_views import OrderWithoutAdminExportView, WaitingForPackingOrdersExportView, \
    WaitingForShippingOrdersExportView, AdminPackingReportExportView, OrderPackageExportView, \
    AdminPackingAllOrdersReportExportView, WaitingForShippingAllOrdersReportExportView, \
    WaitingForPackingAllOrdersReportExportView, AllOrdersWithoutAdminReportExportView, \
    AffiliateAdminOrderPackagesReportExportView
from packing.lists.views import OrderPackageWithoutAdminListView, WaitingForPackingOrdersListView, \
    WaitingForShippingOrdersListView, AdminPackingReportListView, AffiliateAdminOrderPackagesReportListView
from packing.views import OrderPackageApiView, OrderPackageDetailView, AddAdminToOrdersApiView, \
    PackedOrderPackagesApiView, ShippingOrderPackagesApiView, GetOrderPackageView

app_name = 'packing'
urlpatterns = [
    url(r'^orderWithoutAdmin$', OrderPackageWithoutAdminListView.as_view(), name='orderPackageWithoutAdminListView'),
    url(r'^orderWithoutAdmin/(?P<export_type>\S+)', OrderWithoutAdminExportView.as_view(), name=''),
    url(r'^allOrdersWithoutAdminReport/(?P<export_type>\S+)', AllOrdersWithoutAdminReportExportView.as_view(), name=''),

    url(r'^waitingForPackingOrders$', WaitingForPackingOrdersListView.as_view(), name='waitingForPackingOrdersListView'),
    url(r'^waitingForPackingOrders/(?P<export_type>\S+)', WaitingForPackingOrdersExportView.as_view(), name=''),
    url(r'^waitingForPackingAllOrders/(?P<export_type>\S+)', WaitingForPackingAllOrdersReportExportView.as_view(), name=''),

    url(r'^waitingForShippingOrders$', WaitingForShippingOrdersListView.as_view(), name='waitingForShippingOrdersListView'),
    url(r'^waitingForShippingOrders/(?P<export_type>\S+)', WaitingForShippingOrdersExportView.as_view(), name=''),
    url(r'^waitingForShippingOrders/(?P<export_type>\S+)', AffiliateAdminOrderPackagesReportExportView.as_view(), name=''),
    url(r'^waitingForShippingAllOrders/(?P<export_type>\S+)', WaitingForShippingAllOrdersReportExportView.as_view(), name=''),

    url(r'^adminPackingReport$', AdminPackingReportListView.as_view(), name='adminPackingReportListView'),
    url(r'^adminPackingReport/(?P<export_type>\S+)', AdminPackingReportExportView.as_view(), name=''),
    url(r'^adminPackingAllOrdersReport/(?P<export_type>\S+)', AdminPackingAllOrdersReportExportView.as_view(), name=''),

    url(r'^addAdminToOrders$', AddAdminToOrdersApiView.as_view(), name='addAdminToOrdersApiView'),
    url(r'^packedOrderPackages$', PackedOrderPackagesApiView.as_view(), name='packedOrderPackagesApiView'),
    url(r'^shippedOrderPackages$', ShippingOrderPackagesApiView.as_view(), name='shippingOrderPackagesApiView'),
    url(r'^order$', OrderPackageApiView.as_view(), name='orderPackageApiView'),
    url(r'^order/(?P<pk>[0-9]+)$', OrderPackageDetailView.as_view(), name='orderPackageDetailView'),
    url(r'^getOrder/(?P<pk>[0-9]+)$', GetOrderPackageView.as_view(), name='getOrderPackageView'),

    url(r'^orderPackageExport/(?P<export_type>\S+)', OrderPackageExportView.as_view(), name=''),

    url(r'^affiliateAdminOrderPackages$', AffiliateAdminOrderPackagesReportListView.as_view(),
        name='affiliateAdminOrderPackagesReportListView'),
    url(r'^affiliateAdminOrderPackages/(?P<export_type>\S+)', AffiliateAdminOrderPackagesReportExportView.as_view(),
        name=''),

]
