from django.conf.urls import url

from file_handler.list.views import ExtractedPostReportListView, ExtractedPostReportItemListView
from file_handler.views import UploadedFileListCreateView, UploadedFileRetrieveView, UploadedFileWithResponseByTypeView, \
    ExtractPostReportCreateView, UploadedFilePackingWithResponseByTypeView, ExtractEntrancePackageCreateView

app_name = 'file_handler'
urlpatterns = [
    url(r'^upload$', UploadedFileWithResponseByTypeView.as_view(), name='upload'),
    url(r'^uploadPacking', UploadedFilePackingWithResponseByTypeView.as_view(), name='upload'),
    url(r'^retrieve/(?P<pk>[0-9]+)$', UploadedFileRetrieveView.as_view(), name='retrieve'),
    url(r'^extract$', ExtractPostReportCreateView.as_view(), name='extractPostReport'),
    url(r'^extractPacking$', ExtractEntrancePackageCreateView.as_view(), name='extractPacking'),

    url(r'^extractedPostReport/all$', ExtractedPostReportListView.as_view(), name='extractedPostReport'),
    url(r'^extractedPostReportItem/all$', ExtractedPostReportItemListView.as_view(), name='extractedPostReportItem'),

]
