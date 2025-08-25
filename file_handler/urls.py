from django.conf.urls import url

from file_handler.list.views import ExtractedPostReportListView, ExtractedPostReportItemListView, \
    ExtractedEntrancePackageItemListView, ExtractedEntrancePackageListView
from file_handler.views import UploadedFileRetrieveView, UploadedFileWithResponseByTypeView, \
    ExtractPostReportCreateView, UploadedFilePackingWithResponseByTypeView, ExtractEntrancePackageCreateView, \
    ExtractedEntrancePackageDetailView

app_name = 'file_handler'
urlpatterns = [
    url(r'^upload$', UploadedFileWithResponseByTypeView.as_view(), name='upload'),
    url(r'^retrieve/(?P<pk>[0-9]+)$', UploadedFileRetrieveView.as_view(), name='retrieve'),
    url(r'^extract$', ExtractPostReportCreateView.as_view(), name='extractPostReport'),
    url(r'^extractedPostReport/all$', ExtractedPostReportListView.as_view(), name='extractedPostReport'),
    url(r'^extractedPostReportItem/all$', ExtractedPostReportItemListView.as_view(), name='extractedPostReportItem'),


    url(r'^uploadPacking', UploadedFilePackingWithResponseByTypeView.as_view(), name='upload'),
    url(r'^extractPacking$', ExtractEntrancePackageCreateView.as_view(), name='extractPacking'),
    url(r'^extractedEntrancePackage/all$', ExtractedEntrancePackageListView.as_view(),
        name='extractedEntrancePackageList'),
    url(r'^extractedEntrancePackageItem/all$', ExtractedEntrancePackageItemListView.as_view(),
        name='extractedEntrancePackageItemList'),

    url(r'^extractedEntrancePackageDetail/(?P<pk>[0-9]+)$', ExtractedEntrancePackageDetailView.as_view(),
        name='extractedEntrancePackageDetail'),

]
