from datetime import datetime

from django.db import models

from helpers.functions import get_current_user


def custom_upload_to(instance, filename):
    return 'images/{filename}'.format(filename=filename)


class Issue(models.Model):

    BUG = 'bug'
    FEATURE = 'feature'

    TYPE_CHOICES = [
        (BUG, 'باگ'),
        (FEATURE, 'قابلیت جدید'),
    ]

    NEW = 'new'
    IN_PROGRESS = 'in_progress'
    DONE = 'done'

    STATUS_CHOICES = [
        (NEW, 'جدید'),
        (IN_PROGRESS, 'درح حال انجام'),
        (DONE, 'انجام شد'),
    ]

    Low = 1
    MEDIUM = 2
    HIGH = 3

    SEVERITY_CHOICES = [
        (Low, 'اولویت کم'),
        (MEDIUM, 'اولویت متوسط'),
        (HIGH, 'اولویت زیاد'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to=custom_upload_to, null=True, blank=True, default=None)
    issue_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=NEW)
    created_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='issues')
    created_at = models.DateTimeField(blank=True, null=True)

    assigned_to = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_issues',
    )
    is_tested = models.BooleanField(
        default=False,
    )

    severity = models.IntegerField(
        choices=SEVERITY_CHOICES,
        default=MEDIUM,
    )

    def change_status(self, new_status, user=get_current_user() or None):
        if new_status not in dict(self.STATUS_CHOICES):
            raise ValueError(f"Invalid status: {new_status}")

        old_status = self.status
        if old_status == new_status:
            return

        self.status = new_status
        self.save(update_fields=['status'])

        IssueStatusHistory.objects.create(
            issue=self,
            old_status=old_status,
            new_status=new_status,
            changed_by=user,
            changed_at=datetime.now()
        )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_issue_type_display()}: {self.title}"

    def save(self, *args, **kwargs):
        first_register = not self.id
        if first_register:
            self.created_at = datetime.now()
            if not self.created_by:
                self.created_by = get_current_user() or None
        super().save(*args, **kwargs)


class IssueStatusHistory(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='status_history')
    old_status = models.CharField(max_length=20, choices=Issue.STATUS_CHOICES)
    new_status = models.CharField(max_length=20, choices=Issue.STATUS_CHOICES)
    changed_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="User who made the change"
    )
    changed_at = models.DateTimeField()

    class Meta:
        ordering = ['-changed_at']

    def __str__(self):
        who = self.changed_by.get_username() if self.changed_by else "Unknown"
        return f"{self.issue} | {self.get_old_status_display()} → {self.get_new_status_display()} by {who} at {self.changed_at}"
