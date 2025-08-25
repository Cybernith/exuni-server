import zipfile
from django.core.files.base import ContentFile
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.generics import RetrieveAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView


from rest_framework.response import Response

from file_handler.helpers import extract_images_from_excel_and_map_rows_debug
from file_handler.models import UploadedFile, ExtractedPostReport, ExtractedPostReportItem, ExtractedImage, \
    ExtractedEntrancePackageItem, ExtractedEntrancePackage
from file_handler.serializers import UploadedFileSerializer, ExtractPostReportCreateSerializer, \
    ExtractedImageSerializer, ExtractEntrancePackageCreateSerializer, ExtractedEntrancePackageDetailSerializer
from file_handler.services import excel_formatter, extract_number_from_string, sanitize_floats
import pandas as pd

from shop.models import ShopOrder


class UploadedFileListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = UploadedFile.objects.all().order_by("-uploaded_at")
    serializer_class = UploadedFileSerializer
    parser_classes = (MultiPartParser, FormParser)


class UploadedFileRetrieveView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = UploadedFile.objects.all()
    serializer_class = UploadedFileSerializer


class UploadedFileWithResponseByTypeView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = UploadedFileSerializer
    parser_classes = (MultiPartParser, FormParser)

    def create(self, request, *args, **kwargs):
        file_obj = request.FILES.get("file")
        format_type = request.data.get("format_type", "indexed_dict")
        start_col = int(request.data.get("start_col", 1))

        if not file_obj:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            rows_data = excel_formatter(file_obj, start_col=start_col, format_type=format_type)
            rows_data = sanitize_floats(rows_data)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        data = request.data
        data['file_type'] = UploadedFile.POST_REPORT
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        data = serializer.data
        data["rows"] = rows_data

        return Response(data, status=status.HTTP_201_CREATED)


class UploadedFilePackingWithResponseByTypeView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = UploadedFileSerializer
    parser_classes = (MultiPartParser, FormParser)

    def create(self, request, *args, **kwargs):
        file_obj = request.FILES.get("file")
        format_type = request.data.get("format_type", "indexed_dict")
        start_col = int(request.data.get("start_col", 1))

        if not file_obj:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            rows_data = excel_formatter(file_obj, start_col=start_col, format_type=format_type)
            rows_data = sanitize_floats(rows_data)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        data = request.data
        data['file_type'] = UploadedFile.ENTRANCE_PACKAGE
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        instance = serializer.save()

        if instance.file.name.endswith(".xlsx"):
            created_images, row_map, errors = extract_images_from_excel_and_map_rows_debug(instance.file.path, instance)
            response_data = serializer.data
            for i, row in enumerate(rows_data):
                img_instance = row_map.get(i + 1)
                if img_instance:
                    row[0] = img_instance.image.url
                else:
                    row[0] = None
            response_data["rows"] = rows_data

            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response({'message': 'not xlsx file'}, status=status.HTTP_400_BAD_REQUEST)



class ExtractPostReportCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        notif = []
        serializer = ExtractPostReportCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file_id = serializer.validated_data['file_id']
        post_tracking_code_col = serializer.validated_data['post_tracking_code']
        order_col = serializer.validated_data['order']

        uploaded_file = get_object_or_404(UploadedFile, id=file_id)

        try:
            df = pd.read_excel(uploaded_file.file.path)
        except Exception as e:
            return Response({'detail': f'خطا در باز کردن فایل Excel: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

        report = ExtractedPostReport.objects.create(
            name=f"گزارش ارسال به پست {uploaded_file.original_name}",
            uploaded_file=uploaded_file,
        )

        rows_created = 0
        order_shipped = 0

        post_tracking_code_idx = post_tracking_code_col - 1
        order_idx = order_col - 1

        shop_orders_to_update = []

        for idx, row in df.iterrows():
            try:
                code_value = row.iloc[post_tracking_code_idx]
                order_value = row.iloc[order_idx]
                print("code_value:", code_value, flush=True)

                if pd.isna(code_value) or pd.isna(order_value):
                    notif.append(f'{code_value} ساختار کد سفارش معتبر نیست')
                    continue

                order_num = extract_number_from_string(str(order_value))
                if order_num is None:
                    notif.append(f'{code_value} ساختار کد سفارش معتبر نیست')

                if not order_num or not ShopOrder.objects.filter(id=order_num).exists():
                    notif.append(f'{order_value} سفارش معتبر نیست')
                    ExtractedPostReportItem.objects.create(
                        status=ExtractedPostReportItem.ORDER_NOT_AVAILABLE,
                        extracted_report=report,
                        explanation=order_value,
                        post_tracking_code=str(code_value)
                    )
                    rows_created += 1
                else:
                    shop_order = ShopOrder.objects.filter(id=order_num).first()
                    ExtractedPostReportItem.objects.create(
                        status=ExtractedPostReportItem.FOR_ORDER,
                        extracted_report=report,
                        shop_order=shop_order,
                        post_tracking_code=str(code_value)
                    )
                    shop_order.post_tracking_code = str(code_value)
                    shop_orders_to_update.append(shop_order)
                    order_shipped += 1

            except Exception as e:
                notif.append(f'{str(e)} ارور منطق')
                continue

        for order in shop_orders_to_update:
            order.post_tracking_code = str(order.post_tracking_code)
            order.status = ShopOrder.SHIPPED

        ShopOrder.objects.bulk_update(shop_orders_to_update, ['post_tracking_code', 'status'])

        return Response({
            'report_id': report.id,
            'items_created': rows_created + order_shipped,
            'rows_created': rows_created,
            'order_shipped': order_shipped,
            'notifications': notif,
        }, status=status.HTTP_201_CREATED)


class ExtractEntrancePackageCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        serializer = ExtractEntrancePackageCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file_id = serializer.validated_data['file_id']
        selected_headers = serializer.validated_data['selected_headers']

        uploaded_file = get_object_or_404(UploadedFile, id=file_id)

        try:
            df = pd.read_excel(uploaded_file.file.path)
        except Exception as e:
            return Response(
                {'detail': f'خطا در باز کردن فایل Excel: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        package = ExtractedEntrancePackage.objects.create(
            name=f"بسته ورودی {uploaded_file.original_name}",
            uploaded_file=uploaded_file
        )

        rows_created = 0
        notif = []

        for idx, row in df.iterrows():
            try:
                item_data = {}

                for type_key, col_idx in selected_headers.items():
                    if col_idx is None or (col_idx - 1) >= len(row):
                        continue

                    value = row.iloc[col_idx - 1]
                    if pd.isna(value):
                        continue
                    if type_key == ExtractedEntrancePackageItem.PRICE:
                        item_data["price"] = float(value)
                    elif type_key == ExtractedEntrancePackageItem.GROUP_ID:
                        item_data["group_id"] = str(value)
                    elif type_key == ExtractedEntrancePackageItem.NAME:
                        item_data["name"] = str(value)
                    elif type_key == ExtractedEntrancePackageItem.BOX_STACKING:
                        item_data["box_stacking"] = str(value)
                    elif type_key == ExtractedEntrancePackageItem.QUANTITY_PER_BOX:
                        item_data["quantity_per_box"] = int(value)
                    elif type_key == 'bq':
                        item_data["box_quantity"] = int(value)
                    elif type_key == ExtractedEntrancePackageItem.TOTAL_QUANTITY:
                        item_data["total_quantity"] = int(value)
                    elif type_key == ExtractedEntrancePackageItem.TOTAL_AMOUNT:
                        item_data["total_amount"] = float(value)

                if item_data:
                    ExtractedEntrancePackageItem.objects.create(
                        packing=package,
                        image=ExtractedImage.objects.get(uploaded_file=uploaded_file, position=idx + 1).image,
                        **item_data
                    )
                    rows_created += 1

            except Exception as e:
                notif.append(f"سطر {idx}: {str(e)}")

        return Response({
            "package_id": package.id,
            "rows_created": rows_created,
            "notifications": notif,
        }, status=status.HTTP_201_CREATED)


class ExtractedEntrancePackageDetailView(RetrieveAPIView):
    queryset = ExtractedEntrancePackage.objects.all()
    serializer_class = ExtractedEntrancePackageDetailSerializer
