from django.conf.urls import url

from entrance.lists.views import EntrancePackageListView, StoreReceiptListView
from entrance.views import EntrancePackageCreateView, EntrancePackageDetailView, StoreReceiptCreateView, \
    StoreReceiptDetailView, EntrancePackageFileUpdateView, EntrancePackageApiView, EntrancePackageInsertExcelApiView, \
    GetTableOfPackageApiView, PackageDetailView, PackageItemDetailView, UpdatePackageItemsView, RemoveExcelView

app_name = 'entrance'
urlpatterns = [
    url(r'^entrancePackage$', EntrancePackageApiView.as_view(), name='entrancePackageCreate'),
    url(r'^updateEntranceItems$', UpdatePackageItemsView.as_view(), name='updatePackageItems'),
    url(r'^entrancePackage/(?P<pk>[0-9]+)/$', EntrancePackageDetailView.as_view(), name='entrancePackageDetail'),
    url(r'^entrancePackageItem/(?P<pk>[0-9]+)/$', PackageItemDetailView.as_view(), name='entrancePackageItem'),
    url(r'^removeExcel/(?P<pk>[0-9]+)/$', RemoveExcelView.as_view(), name='removeExcelView'),
    url(r'^lists/entrancePackage$', EntrancePackageListView.as_view(), name='entrancePackageListView'),
    url(r'^fileUpload/(?P<pk>[0-9]+)$', EntrancePackageFileUpdateView.as_view(), name='entrancePackageFileUpdateView'),
    url(r'^package/(?P<pk>[0-9]+)$', PackageDetailView.as_view(), name='getTableOfPackageApiView'),
    url(r'^packageTable/(?P<pk>[0-9]+)$', GetTableOfPackageApiView.as_view(), name='getTableOfPackageApiView'),
    url(r'^entrancePackageInsertExcel$', EntrancePackageInsertExcelApiView.as_view(),
        name='entrancePackageInsertExcelApiView'),

    url(r'^storeReceipt$', StoreReceiptCreateView.as_view(), name='storeReceiptCreate'),
    url(r'^storeReceipt/(?P<pk>[0-9]+)/$', StoreReceiptDetailView.as_view(), name='storeReceiptDetail'),
    url(r'^lists/storeReceipt$', StoreReceiptListView.as_view(), name='storeReceiptListView'),
]
