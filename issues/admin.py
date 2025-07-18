from django.contrib import admin

from issues.models import Issue, IssueStatusHistory

admin.site.register(Issue)
admin.site.register(IssueStatusHistory)
