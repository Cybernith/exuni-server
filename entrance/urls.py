from django.conf.urls import url

from entrance.lists.views import EntrancePackageListView
from entrance.views import EntrancePackageCreateView, EntrancePackageDetailView

app_name = 'entrance'
urlpatterns = [
    url(r'^entrancePackage$', EntrancePackageCreateView.as_view(), name='entrancePackageCreate'),
    url(r'^entrancePackage/(?P<pk>[0-9]+)/$', EntrancePackageDetailView.as_view(), name='entrancePackageDetail'),
    url(r'^lists/entrancePackage$', EntrancePackageListView.as_view(), name='entrancePackageListView'),
]
