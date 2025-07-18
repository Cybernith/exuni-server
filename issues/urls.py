from django.conf.urls import url

from issues.lists.views import AdminOwnIssueListView, IssueListView, IssueStatusUpdateAPIView
from issues.views import IssueCreateAPIView, assign_to_self, test_done

app_name = 'issues'
urlpatterns = [
    url(r'^send$', IssueCreateAPIView.as_view(), name='sendIssue'),
    url(r'^own$', AdminOwnIssueListView.as_view(), name='ownIssues'),
    url(r'^all$', IssueListView.as_view(), name='allIssues'),
    url(r'^updateStatus/(?P<pk>[0-9]+)$', IssueStatusUpdateAPIView.as_view(), name='updateStatus'),
    url(r'^assignToSelf/(?P<pk>[0-9]+)$', assign_to_self, name='assignToSelf'),
    url(r'^testDone/(?P<pk>[0-9]+)$', test_done, name='testDone'),

]
