from django.conf.urls import url
from django.urls import path

from affiliate.views import AffiliateFactorCreateApiView

app_name = 'affiliate'
urlpatterns = [
    url(r'^factorCreate$', AffiliateFactorCreateApiView.as_view(), name='affiliateFactorCreateApiView'),

]
