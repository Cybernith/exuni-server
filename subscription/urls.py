from django.conf.urls import url

from subscription.views import TransactionCallbackView, TransactionListCreateView, PlanListView, FactorListView, \
    FactorRetrieveView, BuySubscription, VerifyDiscountCodeView, ExtendSubscription, AddUserView, UserTurnover, \
    BuyExtensions, CompanyExtensionListView

urlpatterns = [
    url(r'callback$', TransactionCallbackView.as_view(), name=''),
    url(r'transactions$', TransactionListCreateView.as_view(), name=''),

    url(r'factors$', FactorListView.as_view(), name=''),
    url(r'factor/(?P<pk>[0-9]+)$', FactorRetrieveView.as_view(), name=''),

    url(r'plans$', PlanListView.as_view(), name=''),

    url(r'buy$', BuyExtensions.as_view(), name=''),
    url(r'extend$', ExtendSubscription.as_view(), name=''),
    url(r'addUser$', AddUserView.as_view(), name=''),
    url(r'companyExtension', CompanyExtensionListView.as_view(), name=''),

    url(r'verifyDiscountCode$', VerifyDiscountCodeView.as_view(), name=''),

    url(r'userTurnover$', UserTurnover.as_view(), name=''),

]
