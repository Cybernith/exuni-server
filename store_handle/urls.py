from django.conf.urls import url

from store_handle.lists.views import NoPackingHandleProductSimpleListView, PackingHandleProductSimpleListView
from store_handle.views import ProductHandleChangeDetailView, ProductPackingInventoryHandleDetailView

app_name = 'store_handle'
urlpatterns = [
    url(r'^productHandleChange/(?P<pk>[0-9]+)$', ProductHandleChangeDetailView.as_view(), name='productHandleChange'),
    url(r'^packingInventoryHandle/(?P<pk>[0-9]+)$', ProductPackingInventoryHandleDetailView.as_view(),
        name='packingInventoryHandle'),
    url(r'^noPackingHandleProducts$', NoPackingHandleProductSimpleListView.as_view(),
        name='noPackingHandleProducts'),
    url(r'^packingHandleProducts$', PackingHandleProductSimpleListView.as_view(),
        name='packingHandleProducts'),

]
