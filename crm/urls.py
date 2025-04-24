from django.conf.urls import url

from crm.list.views import ShopProductViewLogReportListView
from crm.views import ShopProductLogApiView

app_name = 'crm'
urlpatterns = [

    url(r'^shopProductViewLogReport$', ShopProductViewLogReportListView.as_view(), name='shopProductViewLogReport'),
    url(r'^shopProductLog/(?P<product_id>[0-9]+)$', ShopProductLogApiView.as_view(), name='shopProductLog'),

]
