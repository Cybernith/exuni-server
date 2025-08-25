from django.db import models

from helpers.models import EXPLANATION


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


class ExtractedImage(models.Model):
    uploaded_file = models.ForeignKey(UploadedFile, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="excel_images/")
    position = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)


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
    explanation = models.CharField(max_length=255, blank=True, null=True)
    post_tracking_code = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    price = models.IntegerField(default=0)

    def __str__(self):
        return f" {self.post_tracking_code}"


class ExtractedEntrancePackage(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    date = models.DateField(auto_now=True)
    uploaded_file = models.OneToOneField(
        UploadedFile,
        on_delete=models.SET_NULL,
        related_name='entrance_packages',
        limit_choices_to={'file_type': UploadedFile.ENTRANCE_PACKAGE},
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_done = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.date}"


class ExtractedEntrancePackageItem(models.Model):
    PRICE = 'p'
    GROUP_ID = 'g'
    NAME = 'n'
    BOX_STACKING = 'b'
    QUANTITY_PER_BOX = 'qpb'
    TOTAL_QUANTITY = 'tq'
    BOX_QUANTITY = 'bq'
    TOTAL_AMOUNT = 'ta'
    IMAGE = 'img'
    UNKNOWN = 'u'

    INSERT_TYPES = (
        (PRICE, 'قیمت اولیه'),
        (GROUP_ID, 'کد محصول'),
        (NAME, 'نام اولیه'),
        (BOX_STACKING, 'چیدمان جعبه'),
        (QUANTITY_PER_BOX, 'تعداد در هر جعبه'),
        (TOTAL_QUANTITY, 'تعداد کل'),
        (BOX_QUANTITY, 'تعداد جعبه'),
        (TOTAL_AMOUNT, 'مبلغ به تومان'),
        (IMAGE, 'تصویر محصول'),
        (UNKNOWN, 'نامشخص'),
    )

    packing = models.ForeignKey(
        ExtractedEntrancePackage,
        on_delete=models.CASCADE,
        related_name='items'
    )
    image = models.FileField(null=True, blank=True)
    price = models.FloatField(null=True, blank=True)
    group_id = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    box_stacking = models.CharField(max_length=255, null=True, blank=True)
    quantity_per_box = models.PositiveIntegerField(null=True, blank=True)
    box_quantity = models.PositiveIntegerField(null=True, blank=True)
    total_quantity = models.PositiveIntegerField(null=True, blank=True)
    total_amount = models.FloatField(null=True, blank=True)

