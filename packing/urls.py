from django.conf.urls import url

from packing.views import OrderPackageApiView, OrderPackageDetailView

app_name = 'packing'
urlpatterns = [
    url(r'^order$', OrderPackageApiView.as_view(), name='orderPackageApiView'),
    url(r'^order/(?P<pk>[0-9]+)$', OrderPackageDetailView.as_view(), name='orderPackageDetailView'),

]
