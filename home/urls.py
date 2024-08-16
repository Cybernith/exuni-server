from django.conf.urls import url

from rest_framework.routers import DefaultRouter

from home.views import TimeView

router = DefaultRouter()

urlpatterns = router.urls + [
    url(r'^time$', TimeView.as_view(), name='time'),
]
