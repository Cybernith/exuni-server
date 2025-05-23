from django.conf.urls import url

from crm.list.views import ShopProductViewLogReportListView
from crm.views import ShopProductViewLogApiView, ProductVisitReportView, ProductInRangeVisitReportView, \
    UserTopVisitedProductsAPIView, RegisterFinalSearchLogAPIView, CreateNotificationAPIView, \
    UserCurrentNotificationsAPIView, MarkNotificationAsReadView

app_name = 'crm'
urlpatterns = [
    url(r'^shopProductLog/(?P<product_id>[0-9]+)$', ShopProductViewLogApiView.as_view(), name='shopProductLog'),
    url(r'^shopProductViewsSummaryLogReport$', ShopProductViewLogReportListView.as_view(),
        name='shopProductViewsSummaryLogReport'),
    url(r'^shopProductViewsLogReport/(?P<product_id>[0-9]+)$', ProductVisitReportView.as_view(),
        name='shopProductViewsLogReport'),
    url(r'^shopProductViewsInRangeLogReport/(?P<product_id>[0-9]+)$', ProductInRangeVisitReportView.as_view(),
        name='shopProductViewsLogReport'),
    url(r'^userTopVisitedProducts$', UserTopVisitedProductsAPIView.as_view(),
        name='userTopVisitedProducts'),
    url(r'^registerFinalSearchLog$', RegisterFinalSearchLogAPIView.as_view(),
        name='registerFinalSearchLog'),
    url(r'^createNotification$', CreateNotificationAPIView.as_view(),
        name='createNotification'),
    url(r'^retrieveNotification$', UserCurrentNotificationsAPIView.as_view(),
        name='retrieveNotification'),
    url(r'^markNotificationAsRead/(?P<notification_id>[0-9]+)$', MarkNotificationAsReadView.as_view(),
        name='markNotificationAsRead'),
]
