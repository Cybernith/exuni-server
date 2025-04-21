from django.conf.urls import url

from shop.views import CurrentUserCartApiView, CartDetailView

app_name = 'shop'
urlpatterns = [
    url(r'^currentUserCart$', CurrentUserCartApiView.as_view(), name='currentUserCart'),
    url(r'^cart/(?P<pk>[0-9]+)$', CartDetailView.as_view(), name='cartDetail'),

]
