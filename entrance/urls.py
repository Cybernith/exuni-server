from django.conf.urls import url

from entrance.lists.views import EntrancePackageListView, StoreReceiptListView
from entrance.views import EntrancePackageCreateView, EntrancePackageDetailView, StoreReceiptCreateView, \
    StoreReceiptDetailView, EntrancePackageFileUpdateView, EntrancePackageApiView, EntrancePackageInsertExcelApiView, \
    GetTableOfPackageApiView, PackageDetailView, PackageItemDetailView, UpdatePackageItemsView, RemoveExcelView, \
    StorePackagesView, StoreReceiptApiView, StoreReceiptDetail, CreateReceiptsItemsView, SupplierRemainItems, \
    SupplierStoreReceiptsView

app_name = 'entrance'
urlpatterns = [
    url(r'^entrancePackage$', EntrancePackageApiView.as_view(), name='entrancePackageCreate'),
    url(r'^updateEntranceItems$', UpdatePackageItemsView.as_view(), name='updatePackageItems'),
    url(r'^entrancePackage/(?P<pk>[0-9]+)/$', EntrancePackageDetailView.as_view(), name='entrancePackageDetail'),
    url(r'^storeEntrancePackages/(?P<pk>[0-9]+)/$', StorePackagesView.as_view(), name='storePackages'),
    url(r'^entrancePackageItem/(?P<pk>[0-9]+)/$', PackageItemDetailView.as_view(), name='entrancePackageItem'),
    url(r'^removeExcel/(?P<pk>[0-9]+)/$', RemoveExcelView.as_view(), name='removeExcel'),
    url(r'^lists/entrancePackage$', EntrancePackageListView.as_view(), name='entrancePackageList'),
    url(r'^fileUpload/(?P<pk>[0-9]+)$', EntrancePackageFileUpdateView.as_view(), name='entrancePackageFileUpdate'),
    url(r'^package/(?P<pk>[0-9]+)$', PackageDetailView.as_view(), name='getTableOfPackageApi'),
    url(r'^packageTable/(?P<pk>[0-9]+)$', GetTableOfPackageApiView.as_view(), name='getTableOfPackageApi'),
    url(r'^entrancePackageInsertExcel$', EntrancePackageInsertExcelApiView.as_view(),
        name='entrancePackageInsertExcelApiView'),

    url(r'^storeReceipt$', StoreReceiptCreateView.as_view(), name='storeReceiptCreate'),
    url(r'^createReceiptsItems$', CreateReceiptsItemsView.as_view(), name='createReceiptsItems'),
    url(r'^submitStoreReceipt$', StoreReceiptApiView.as_view(), name='storeReceiptApiView'),
    url(r'^storeReceipt/(?P<pk>[0-9]+)/$', StoreReceiptDetailView.as_view(), name='storeReceiptDetail'),
    url(r'^lists/storeReceipt$', StoreReceiptListView.as_view(), name='storeReceiptList'),
    url(r'^receipt/(?P<pk>[0-9]+)$', StoreReceiptDetail.as_view(), name='storeReceiptDetail'),
    url(r'^supplierPackageRemain/(?P<pk>[0-9]+)$', SupplierRemainItems.as_view(), name='supplierRemainItems'),
    url(r'^supplierStoreReceipts/(?P<pk>[0-9]+)$', SupplierStoreReceiptsView.as_view(), name='supplierStoreReceiptsView'),
]
