from django.conf.urls import url

from subscription.export_views import UserTurnoverListExportView, SubscriptionFactorListExportView, \
    SubscriptionFactorDetailExportView
from subscription.views import TransactionCallbackView, TransactionListCreateView, FactorListView, \
    FactorRetrieveView, VerifyDiscountCodeView, UserTurnover
urlpatterns = [
    url(r'callback$', TransactionCallbackView.as_view(), name=''),
    url(r'transactions$', TransactionListCreateView.as_view(), name=''),

    url(r'factors$', FactorListView.as_view(), name=''),
    url(r'factor/(?P<pk>[0-9]+)$', FactorRetrieveView.as_view(), name=''),

    url(r'verifyDiscountCode$', VerifyDiscountCodeView.as_view(), name=''),

    url(r'userTurnover$', UserTurnover.as_view(), name=''),
    url(r'^userTurnover/all/(?P<export_type>\S+)', UserTurnoverListExportView.as_view(), name=''),
    url(r'^factors/(?P<export_type>\S+)', SubscriptionFactorListExportView.as_view(), name=''),
    url(r'^factorDetail/(?P<export_type>\S+)', SubscriptionFactorDetailExportView.as_view(), name=''),

]
