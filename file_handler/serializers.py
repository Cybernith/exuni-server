from rest_framework import serializers

from file_handler.models import UploadedFile, ExtractedPostReportItem, ExtractedPostReport, ExtractedImage, \
    ExtractedEntrancePackage, ExtractedEntrancePackageItem


class ExtractedImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExtractedImage
        fields = ["id", "image", "position", "uploaded_at"]


class UploadedFileSerializer(serializers.ModelSerializer):
    images = ExtractedImageSerializer(many=True, read_only=True)

    class Meta:
        model = UploadedFile
        fields = ["id", "file", "file_type", "original_name", "size", "uploaded_at", "images"]
        read_only_fields = ["id", "original_name", "size", "uploaded_at", "images"]


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
            'explanation',
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


class ExtractEntrancePackageCreateSerializer(serializers.Serializer):
    file_id = serializers.IntegerField()
    selected_headers = serializers.DictField()


class ExtractedEntrancePackageReportSerializer(serializers.ModelSerializer):
    items_count = serializers.SerializerMethodField()

    class Meta:
        model = ExtractedEntrancePackage
        fields = [
            'id',
            'name',
            'date',
            'created_at',
            'updated_at',
            'items_count'
        ]
        read_only_fields = ['created_at', 'updated_at', 'items_count']

    def get_items_count(self, obj):
        return obj.items.all().count()


class ExtractedEntrancePackageItemSerializer(serializers.ModelSerializer):
    pic = serializers.SerializerMethodField()
    total = serializers.SerializerMethodField()

    class Meta:
        model = ExtractedEntrancePackageItem
        fields = '__all__'
        read_only_fields = ['created_at']

    def get_pic(self, obj):
        return obj.image.url if obj.image else None

    def get_total(self, obj):
        if obj.total_quantity:
            return obj.total_quantity
        qpb = obj.quantity_per_box if obj.quantity_per_box else 1
        bq = obj.box_quantity if obj.box_quantity else 1
        return qpb * bq


class ExtractedEntrancePackageDetailSerializer(serializers.ModelSerializer):
    items_count = serializers.SerializerMethodField()
    items = ExtractedEntrancePackageItemSerializer(many=True, read_only=True)

    class Meta:
        model = ExtractedEntrancePackage
        fields = [
            'id',
            'name',
            'date',
            'created_at',
            'updated_at',
            'items_count',
            'items',
        ]
        read_only_fields = ['created_at', 'updated_at', 'items_count']

    def get_items_count(self, obj):
        return obj.items.count()


