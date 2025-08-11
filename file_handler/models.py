from django.db import models


def custom_upload_to(instance, filename):
    return 'images/{filename}'.format(filename=filename)


class UploadedFile(models.Model):
    ENTRANCE_PACKAGE = 'entrance_packages'
    POST_REPORT = 'post_report'

    FILE_TYPES = (
        (ENTRANCE_PACKAGE, ' پکیج ورودی'),
        (POST_REPORT, ' گزارش پست'),
    )

    file = models.FileField(upload_to=custom_upload_to)
    file_type = models.CharField(max_length=55, choices=FILE_TYPES)
    original_name = models.CharField(max_length=255, blank=True)
    size = models.PositiveIntegerField()  # bytes
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.file:
            self.original_name = self.file.name
            self.size = self.file.size
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_file_type_display()} - {self.original_name}"


class ExtractedPostReport(models.Model):
    name = models.CharField(max_length=255)
    date = models.DateField(auto_now=True)
    uploaded_file = models.OneToOneField(
        UploadedFile,
        on_delete=models.CASCADE,
        related_name='extracted_post_report',
        limit_choices_to={'file_type': UploadedFile.POST_REPORT}
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.date}"


class ExtractedPostReportItem(models.Model):
    FOR_ORDER = 'f'
    ORDER_NOT_AVAILABLE = 'n'

    TYPES = (
        (FOR_ORDER, ' سفارش'),
        (ORDER_NOT_AVAILABLE, ' نا معلوم'),
    )

    status = models.CharField(choices=TYPES, max_length=1, default=ORDER_NOT_AVAILABLE)
    extracted_report = models.ForeignKey(
        ExtractedPostReport,
        on_delete=models.CASCADE,
        related_name='items'
    )
    shop_order = models.ForeignKey(
        'shop.ShopOrder',
        on_delete=models.CASCADE,
        related_name='post_report_items',
        blank=True,
        null=True,
    )
    post_tracking_code = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    price = models.IntegerField(default=0)

    def __str__(self):
        return f" {self.post_tracking_code}"
