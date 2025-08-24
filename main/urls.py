from django.conf.urls import url
from django.urls import path

from main.lists.views import BusinessListView, StoreListView, CurrencyListView, SupplierListView
from main.store_keeping.views import StoreKeepingStoreListView, StoreKeepingStoreApiView, StoreKeepingStoreDetailView
from main.views import BusinessApiView, BusinessDetailView, StoreApiView, StoreDetailView, CurrencyApiView, \
    CurrencyDetailView, SupplierApiView, SupplierDetailView, CurrencyListCreate, CurrencyCRUD, StorekeeperApiView, \
    SupplierAdminsApiView, BusinessOwnersApiView, BusinessLogoUpdateView, BusinessOwnerNationalCardPictureUpdateView, \
    BusinessByTokenDetailView, PackingAdminApiView

app_name = 'main'
urlpatterns = [
    url(r'^business$', BusinessApiView.as_view(), name='businessApiView'),
    url(r'^business/(?P<pk>[0-9]+)$', BusinessDetailView.as_view(), name='BusinessDetailView'),
    path('businessByToken/<str:token>', BusinessByTokenDetailView.as_view(), name='businessByTokenDetailView'),
    url(r'^business/all$', BusinessListView.as_view(), name='businessListView'),
    url(r'^businessOwner/all$', BusinessOwnersApiView.as_view(), name='businessOwnersApiView'),
    url(r'^businessLogoUpdate/(?P<pk>[0-9]+)$', BusinessLogoUpdateView.as_view(), name='businessLogoUpdateView'),
    url(r'^businessOwnerNationalCardPictureUpdate/(?P<pk>[0-9]+)$',
        BusinessOwnerNationalCardPictureUpdateView.as_view(), name='businessOwnerNationalCardPictureUpdateView'),

    url(r'^store$', StoreApiView.as_view(), name='storeApiView'),
    url(r'^store/(?P<pk>[0-9]+)$', StoreDetailView.as_view(), name='storeDetailView'),
    url(r'^store/all$', StoreListView.as_view(), name='storeListView'),
    url(r'^storekeeper/all$', StorekeeperApiView.as_view(), name='storekeeperApiView'),
    url(r'^packingAdmin/all$', PackingAdminApiView.as_view(), name='packingAdminApiView'),

    url(r'^currency$', CurrencyApiView.as_view(), name='currencyApiView'),
    url(r'^currency/(?P<pk>[0-9]+)$', CurrencyDetailView.as_view(), name='currencyDetailView'),
    url(r'^currency/all$', CurrencyListView.as_view(), name='currencyListView'),
    url(r'^currencyForm/$', CurrencyListCreate.as_view(), name='currencyListCreate'),
    path('currencyForm/<int:pk>/', CurrencyCRUD.as_view(), name='currencyCRUD'),

    url(r'^supplier$', SupplierApiView.as_view(), name='supplierApiView'),
    url(r'^supplier/(?P<pk>[0-9]+)$', SupplierDetailView.as_view(), name='supplierDetailView'),
    url(r'^supplier/all$', SupplierListView.as_view(), name='supplierListView'),
    url(r'^supplierAdmin/all$', SupplierAdminsApiView.as_view(), name='supplierAdminsApiView'),

    # store keeping
    url(r'^storeKeepingStore$', StoreKeepingStoreApiView.as_view(), name='storeKeepingStoreApi'),
    url(r'^storeKeepingStore/(?P<pk>[0-9]+)$', StoreKeepingStoreDetailView.as_view(), name='storeKeepingStoreDetail'),
    url(r'^storeKeepingStore/all$', StoreKeepingStoreListView.as_view(), name='storeKeepingStoreList'),

]
