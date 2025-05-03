from django.conf.urls import url

from crm.list.views import ShopProductViewLogReportListView
from crm.views import ShopProductViewLogApiView, ProductVisitReportView, ProductInRangeVisitReportView, \
    UserTopVisitedProductsAPIView, RegisterFinalSearchLogAPIView, CreateNotificationAPIView, \
    UserCurrentNotificationsAPIView

app_name = 'financial_management'
urlpatterns = [
    # url(r'^shopProductLog/(?P<product_id>[0-9]+)$', ShopProductViewLogApiView.as_view(), name='shopProductLog'),
]
