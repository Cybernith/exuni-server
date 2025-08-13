from rest_framework import serializers

from file_handler.models import UploadedFile, ExtractedPostReportItem, ExtractedPostReport
from shop.api_serializers import ApiCustomerShopOrderItemSerializer, ApiCustomerShopOrderSimpleSerializer


class UploadedFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedFile
        fields = ["id", "file", "file_type", "original_name", "size", "uploaded_at"]
        read_only_fields = ["id", "original_name", "size", "uploaded_at"]


class ExtractPostReportCreateSerializer(serializers.Serializer):
    file_id = serializers.IntegerField()
    post_tracking_code = serializers.IntegerField()
    order = serializers.IntegerField()


class ExtractedPostReportItemSerializer(serializers.ModelSerializer):
    status_display = serializers.SerializerMethodField()

    class Meta:
        model = ExtractedPostReportItem
        fields = [
            'id',
            'status',
            'status_display',
            'post_tracking_code',
            'created_at'
        ]
        read_only_fields = ['created_at']

    def get_status_display(self, obj):
        return obj.get_status_display()


class ExtractedPostReportSerializer(serializers.ModelSerializer):
    items_count = serializers.SerializerMethodField()

    class Meta:
        model = ExtractedPostReport
        fields = [
            'id',
            'name',
            'date',
            'uploaded_file',
            'created_at',
            'updated_at',
            'items_count'
        ]
        read_only_fields = ['created_at', 'updated_at', 'items_count']

    def get_items_count(self, obj):
        return obj.items.filter(status=ExtractedPostReportItem.ORDER_NOT_AVAILABLE).count()
