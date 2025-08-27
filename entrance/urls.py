from django.conf.urls import url

from entrance.lists.views import EntrancePackageListView, StoreReceiptListView, ChinaEntrancePackagePackageListView, \
    PendingChinaEntrancePackagePackageListView, InsertedPackageDeliveryItemListView, \
    ChinaEntrancePackageDeliveryListView
from entrance.views import EntrancePackageCreateView, EntrancePackageDetailView, StoreReceiptCreateView, \
    StoreReceiptDetailView, EntrancePackageFileUpdateView, EntrancePackageApiView, EntrancePackageInsertExcelApiView, \
    GetTableOfPackageApiView, PackageDetailView, PackageItemDetailView, UpdatePackageItemsView, RemoveExcelView, \
    StorePackagesView, StoreReceiptApiView, StoreReceiptDetail, CreateReceiptsItemsView, SupplierRemainItems, \
    SupplierStoreReceiptsView, CreateChinaEntrancePackageFromExtracted, ChinaEntrancePackageDetailView, \
    PendingChinaEntrancePackageDetailView, ChinaEntrancePackageDeliveryCreateView, \
    ChinaEntrancePackageDeliveryItemsUpdateView, ChinaEntrancePackageDeliveryItemInsertView

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

    url(r'^createChinaEntrancePackageFromExtracted/(?P<pk>[0-9]+)$', CreateChinaEntrancePackageFromExtracted.as_view(),
        name='CreateChinaEntrancePackageFromExtracted'),
    url(r'^chinaEntrancePackage/all$', ChinaEntrancePackagePackageListView.as_view(),
        name='chinaEntrancePackageList'),

    url(r'^deliveries/create$', ChinaEntrancePackageDeliveryCreateView.as_view(),
        name='chinaEntrancePackageDeliveryCreate'),


    url(r'^chinaEntrancePackage/(?P<pk>[0-9]+)$', ChinaEntrancePackageDetailView.as_view(),
        name='chinaEntrancePackagePackageDetail'),

    url(r'^pendingChinaEntrancePackage/all$', PendingChinaEntrancePackagePackageListView.as_view(),
        name='pendingChinaEntrancePackageList'),
    url(r'^pendingChinaEntrancePackage/(?P<pk>[0-9]+)$', PendingChinaEntrancePackageDetailView.as_view(),
        name='pendingChinaEntrancePackage'),

    url(r'^deliveries/create$', ChinaEntrancePackageDeliveryCreateView.as_view(),
        name='chinaEntrancePackageDeliveryCreate'),

    url(r'^deliveries/insert/(?P<pk>[0-9]+)$', ChinaEntrancePackageDeliveryItemsUpdateView.as_view(),
        name='deliveriesInsert'),

    url(r'^deliveriesItem/insert/(?P<id>[0-9]+)$', ChinaEntrancePackageDeliveryItemInsertView.as_view(),
        name='deliveriesItemInsert'),

    url(r'^insertedPackageDeliveryItem/all$', InsertedPackageDeliveryItemListView.as_view(),
        name='insertedPackageDeliveryItem'),

    url(r'^chinaEntrancePackageDelivery/all$', ChinaEntrancePackageDeliveryListView.as_view(),
        name='chinaEntrancePackageDelivery'),

]
