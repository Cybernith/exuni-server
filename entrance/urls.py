from django.conf.urls import url

from entrance.lists.views import EntrancePackageListView, StoreReceiptListView
from entrance.views import EntrancePackageCreateView, EntrancePackageDetailView, StoreReceiptCreateView, \
    StoreReceiptDetailView

app_name = 'entrance'
urlpatterns = [
    url(r'^entrancePackage$', EntrancePackageCreateView.as_view(), name='entrancePackageCreate'),
    url(r'^entrancePackage/(?P<pk>[0-9]+)/$', EntrancePackageDetailView.as_view(), name='entrancePackageDetail'),
    url(r'^lists/entrancePackage$', EntrancePackageListView.as_view(), name='entrancePackageListView'),

    url(r'^storeReceipt$', StoreReceiptCreateView.as_view(), name='storeReceiptCreate'),
    url(r'^storeReceipt/(?P<pk>[0-9]+)/$', StoreReceiptDetailView.as_view(), name='storeReceiptDetail'),
    url(r'^lists/storeReceipt$', StoreReceiptListView.as_view(), name='storeReceiptListView'),
]
