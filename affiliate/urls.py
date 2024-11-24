from django.conf.urls import url
from django.urls import path

from affiliate.views import AffiliateFactorCreateApiView, AffiliateProductsRetrieveView, \
    AffiliateReceiveProductsInventoryView, AffiliateFactorPaymentApiView, AffiliateCustomersView

from affiliate.lists.views import AffiliateFactorListView, AffiliateCustomersListView

app_name = 'affiliate'
urlpatterns = [
    url(r'^factorCreate$', AffiliateFactorCreateApiView.as_view(), name='affiliateFactorCreateApiView'),
    url(r'^factor/all$', AffiliateFactorListView.as_view(), name='affiliateFactorListView'),
    url(r'^productsRetrieve$', AffiliateProductsRetrieveView.as_view(), name='affiliateProductsRetrieveView'),
    url(r'^receiveProductsInventory$', AffiliateReceiveProductsInventoryView.as_view(),
        name='affiliateReceiveProductsInventoryView'),

    url(r'^factorPayment$', AffiliateFactorPaymentApiView.as_view(), name='affiliateFactorPaymentApiView'),
    url(r'^customers$', AffiliateCustomersListView.as_view(), name='affiliateCustomersListView'),

]
