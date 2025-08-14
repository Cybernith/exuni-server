from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include
from rest_framework.permissions import AllowAny

from rest_framework.schemas import get_schema_view
from rest_framework_swagger.renderers import SwaggerUIRenderer, OpenAPIRenderer

from helpers.views.TestApiView import TestApiView
from products.torob.views import TorobProductAPIView
from server.health_check_view import health_check
from users.views.auth_views import ObtainAuthTokenView
from server import settings
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
...

# Create our schema's view w/ the get_schema_view() helper method. Pass in the proper Renderers for swagger
schema_view = get_schema_view(title='Users API', renderer_classes=[OpenAPIRenderer, SwaggerUIRenderer])

urlpatterns = [
    url('test', TestApiView.as_view()),

    url(r'^home/', include('home.urls')),

    url(r'^login$', ObtainAuthTokenView.as_view(), name='login'),
    url(r'^users/', include('users.urls')),
    url(r'^main/', include('main.urls')),
    url(r'^product/', include('products.urls')),
    url(r'^entrance/', include('entrance.urls')),
    url(r'^affiliate/', include('affiliate.urls')),
    url(r'^subscriptions/', include('subscription.urls')),
    url(r'^packing/', include('packing.urls')),
    url(r'^reports/', include('reports.urls')),
    url(r'^shop/', include('shop.urls')),
    url(r'^cms/', include('cms.urls')),
    url(r'^crm/', include('crm.urls')),
    url(r'^finance/', include('financial_management.urls')),
    url(r'^api/', include('shop.shop_api_urls')),
    url(r'^issues/', include('issues.urls')),
    url(r'^store_handle/', include('store_handle.urls')),
    url(r'^file_handler/', include('file_handler.urls')),

    path('admin/', admin.site.urls),
    path('nested_admin/', include('nested_admin.urls')),
    path('schema/shop/', SpectacularAPIView.as_view(permission_classes=[AllowAny]), name='schema-shop'),
    path('schema/shop/swagger/', SpectacularSwaggerView.as_view(url_name='schema-shop', permission_classes=[AllowAny]),
         name='swagger-ui-shop'),

    url(r'^torob_api/v3/products$', TorobProductAPIView.as_view(), name='torobApi'),
    path('v2/health-check', health_check),

    path('schema', SpectacularAPIView.as_view(permission_classes=[AllowAny]), name='schema-login'),
    path('docs', SpectacularSwaggerView.as_view(url_name='schema-login', permission_classes=[AllowAny]),
         name='swagger-ui-login'),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
