from django.conf.urls import url

from subscription.views import TransactionCallbackView, TransactionListCreateView, FactorListView, \
    FactorRetrieveView, VerifyDiscountCodeView, UserTurnover
urlpatterns = [
    url(r'callback$', TransactionCallbackView.as_view(), name=''),
    url(r'transactions$', TransactionListCreateView.as_view(), name=''),

    url(r'factors$', FactorListView.as_view(), name=''),
    url(r'factor/(?P<pk>[0-9]+)$', FactorRetrieveView.as_view(), name=''),

    url(r'verifyDiscountCode$', VerifyDiscountCodeView.as_view(), name=''),

    url(r'userTurnover$', UserTurnover.as_view(), name=''),

]
