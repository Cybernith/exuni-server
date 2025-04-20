"""server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include

from rest_framework.schemas import get_schema_view
from rest_framework_swagger.renderers import SwaggerUIRenderer, OpenAPIRenderer

from helpers.views.TestApiView import TestApiView
from users.views.auth_views import ObtainAuthTokenView
from server import settings

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

    path('admin/', admin.site.urls),



]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
