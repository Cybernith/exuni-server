from django.conf.urls import url

from store_handle.lists.views import NoPackingHandleProductSimpleListView, PackingHandleProductSimpleListView, \
    WaitForStoreHandleProductSimpleListView, StoreHandleProductSimpleListView, StoreInventoryListView, \
    StoreNoInfoProductSimpleListView
from store_handle.views import ProductHandleChangeDetailView, ProductPackingInventoryHandleDetailView, \
    ProductStoreInventoryHandleCreateAPIView, ProductStoreInventoryUpdateAPIView, InventoryTransferViewSet, \
    InventoryTransferCreateView, ProductStoreInfoDetailView

app_name = 'store_handle'
urlpatterns = [
    url(r'^productHandleChange/(?P<pk>[0-9]+)$', ProductHandleChangeDetailView.as_view(), name='productHandleChange'),
    url(r'^packingInventoryHandle/(?P<pk>[0-9]+)$', ProductPackingInventoryHandleDetailView.as_view(),
        name='packingInventoryHandle'),
    url(r'^noPackingHandleProducts$', NoPackingHandleProductSimpleListView.as_view(),
        name='noPackingHandleProducts'),
    url(r'^packingHandleProducts$', PackingHandleProductSimpleListView.as_view(),
        name='packingHandleProducts'),

    url(r'^waitForStoreHandleProducts$', WaitForStoreHandleProductSimpleListView.as_view(),
        name='waitForStoreHandleProducts'),
    url(r'^storeHandleProducts$', StoreHandleProductSimpleListView.as_view(),
        name='storeHandleProducts'),

    url(r'^productStoreInventoryHandleCreate$', ProductStoreInventoryHandleCreateAPIView.as_view(),
        name='productStoreInventoryHandleCreate'),
    url(r'^storeInventoryUpdate/(?P<pk>[0-9]+)$', ProductStoreInventoryUpdateAPIView.as_view(),
        name='storeInventoryUpdate'),

    url(r'^inventoryTransfers$', InventoryTransferViewSet.as_view({'get': 'list'}), name='inventoryTransfers'),
    url(r'^inventoryTransferCreate$', InventoryTransferCreateView.as_view(), name='inventoryTransferCreate'),
    url(r'^storeInventoryList$', StoreInventoryListView.as_view(),
        name='storeInventoryList'),

    url(r'^productStoreInfo/(?P<pk>[0-9]+)$', ProductStoreInfoDetailView.as_view(), name='productStoreInfo'),
    url(r'^storeNoInfoProductList$', StoreNoInfoProductSimpleListView.as_view(),
        name='storeNoInfoProductList'),

]
