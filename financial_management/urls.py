from django.conf.urls import url

from financial_management.views import StartZarinpalPaymentApiView, ZarinpalCallbackApiView, StartPaymentApiView, \
    PaymentCallbackApiView, VerifyDiscountCodeView, StartZarinpalWalletTopUPApiView, ZarinpalTopUpWalletCallbackApiView, \
    DiscountCheckAPIView

app_name = 'financial_management'
urlpatterns = [
    url(r'^zarinpalPaymentStart/(?P<order_id>[0-9]+)$', StartZarinpalPaymentApiView.as_view(), name='zarinpal_start'),
    url(r'^zarinpalPaymentCallback$', ZarinpalCallbackApiView.as_view(), name='zarinpal_callback'),

    url(r'^zarinpalTopUpWalletStart$', StartZarinpalWalletTopUPApiView.as_view(), name='zarinpal_top_up_wallet_start'),
    url(r'^zarinpalTopUpWalletCallback$', ZarinpalTopUpWalletCallbackApiView.as_view(),
        name='zarinpal_top_up_wallet_callback'),

    url(r'^paymentStart/(?P<order_id>[0-9]+)$', StartPaymentApiView.as_view(), name='startPayment'),
    url(r'^paymentCallback$', PaymentCallbackApiView.as_view(), name='paymentCallback'),

    url(r'verifyDiscountCode$', VerifyDiscountCodeView.as_view(), name=''),
    url(r'discountCheck$', DiscountCheckAPIView.as_view(), name='discountCheck'),
]
