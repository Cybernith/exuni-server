from rest_framework import serializers

from file_handler.models import UploadedFile


class UploadedFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedFile
        fields = ["id", "file", "file_type", "original_name", "size", "uploaded_at"]
        read_only_fields = ["id", "original_name", "size", "uploaded_at"]


class ExtractPostReportCreateSerializer(serializers.Serializer):
    file_id = serializers.IntegerField()
    post_tracking_code = serializers.IntegerField()
    order = serializers.IntegerField()

