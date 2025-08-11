from django.contrib import admin
from file_handler.models import ExtractedPostReport, ExtractedPostReportItem, UploadedFile


@admin.register(ExtractedPostReport)
class ExtractedPostReportAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "date", "uploaded_file", "created_at", "updated_at")
    list_filter = ("date", "created_at", "updated_at")
    search_fields = ("name", "uploaded_file__original_name")
    readonly_fields = ("created_at", "updated_at")


@admin.register(ExtractedPostReportItem)
class ExtractedPostReportItemAdmin(admin.ModelAdmin):
    list_display = ("id", "extracted_report", "shop_order", "post_tracking_code", "price", "created_at")
    list_filter = ("created_at",)
    search_fields = ("post_tracking_code", "shop_order__id")
    readonly_fields = ("created_at",)


@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ("id", "original_name", "file_type", "size", "uploaded_at")
    list_filter = ("file_type", "uploaded_at")
