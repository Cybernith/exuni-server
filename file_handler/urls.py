from django.conf.urls import url

from file_handler.views import UploadedFileListCreateView, UploadedFileRetrieveView, UploadedFileWithResponseByTypeView, \
    ExtractPostReportCreateView

app_name = 'file_handler'
urlpatterns = [
    url(r'^upload$', UploadedFileWithResponseByTypeView.as_view(), name='upload'),
    url(r'^retrieve/(?P<pk>[0-9]+)$', UploadedFileRetrieveView.as_view(), name='retrieve'),
    url(r'^extract$', ExtractPostReportCreateView.as_view(), name='extractPostReport'),
]
