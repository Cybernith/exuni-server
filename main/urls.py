from django.conf.urls import url
from django.urls import path

from main.lists.views import BusinessListView, StoreListView, CurrencyListView, SupplierListView
from main.views import BusinessApiView, BusinessDetailView, StoreApiView, StoreDetailView, CurrencyApiView, \
    CurrencyDetailView, SupplierApiView, SupplierDetailView, CurrencyListCreate, CurrencyCRUD

app_name = 'main'
urlpatterns = [
    url(r'^business$', BusinessApiView.as_view(), name='businessApiView'),
    url(r'^business/(?P<pk>[0-9]+)$', BusinessDetailView.as_view(), name='BusinessDetailView'),
    url(r'^business/all$', BusinessListView.as_view(), name='businessListView'),

    url(r'^store$', StoreApiView.as_view(), name='storeApiView'),
    url(r'^store/(?P<pk>[0-9]+)$', StoreDetailView.as_view(), name='storeDetailView'),
    url(r'^store/all$', StoreListView.as_view(), name='storeListView'),

    url(r'^currency$', CurrencyApiView.as_view(), name='currencyApiView'),
    url(r'^currency/(?P<pk>[0-9]+)$', CurrencyDetailView.as_view(), name='currencyDetailView'),
    url(r'^currency/all$', CurrencyListView.as_view(), name='currencyListView'),
    url(r'^currencyForm/$', CurrencyListCreate.as_view(), name='currencyListCreate'),
    path('currencyForm/<int:pk>/', CurrencyCRUD.as_view(), name='currencyCRUD'),

    url(r'^supplier$', SupplierApiView.as_view(), name='supplierApiView'),
    url(r'^supplier/(?P<pk>[0-9]+)$', SupplierDetailView.as_view(), name='supplierDetailView'),
    url(r'^supplier/all$', SupplierListView.as_view(), name='supplierListView'),

]
