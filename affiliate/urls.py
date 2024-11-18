from django.conf.urls import url
from django.urls import path

from affiliate.views import AffiliateFactorCreateApiView

from affiliate.lists.views import AffiliateFactorListView

app_name = 'affiliate'
urlpatterns = [
    url(r'^factorCreate$', AffiliateFactorCreateApiView.as_view(), name='affiliateFactorCreateApiView'),
    url(r'^factor/all$', AffiliateFactorListView.as_view(), name='affiliateFactorListView'),

]
