from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView


from rest_framework.response import Response


from file_handler.models import UploadedFile, ExtractedPostReport, ExtractedPostReportItem
from file_handler.serializers import UploadedFileSerializer, ExtractPostReportCreateSerializer
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
            name=f"گزارش ارسال به پست {file_id}",
            uploaded_file=uploaded_file,
        )

        rows_created = 0
        order_shipped = 0

        post_tracking_code_idx = post_tracking_code_col - 1
        order_idx = order_col - 1

        for idx, row in df.iterrows():
            try:
                code_value = row.iloc[post_tracking_code_idx]
                order_value = row.iloc[order_idx]
                print("code_value:", code_value, flush=True)

                if pd.isna(code_value) or pd.isna(order_value):
                    notif.append(f'{code_value} ساختار کد سفارش معتبر  نیست')
                    continue

                order_num = extract_number_from_string(str(order_value))
                if order_num is None:
                    notif.append(f'{code_value} ساختار کد سفارش معتبر نیست')
                    continue

                shop_order = ShopOrder.objects.filter(id=order_num).first()
                if not shop_order:
                    notif.append(f'{order_value} سفارش معتبر نیست')
                    ExtractedPostReportItem.objects.create(
                        status=ExtractedPostReportItem.ORDER_NOT_AVAILABLE,
                        extracted_report=report,
                        post_tracking_code=str(code_value)
                    )
                    rows_created += 1

                else:
                    ExtractedPostReportItem.objects.create(
                        status=ExtractedPostReportItem.FOR_ORDER,
                        extracted_report=report,
                        shop_order=shop_order,
                        post_tracking_code=str(code_value)
                    )
                    shop_order.update(post_tracking_code=str(code_value))
                    shop_order.ship_order()
                    order_shipped += 1


            except Exception as e:
                notif.append(f'{str(e)} ارور منطق')
                continue

        return Response({
            'report_id': report.id,
            'items_created': rows_created + order_shipped,
            'rows_created': rows_created,
            'order_shipped': order_shipped,
            'notifications': notif,
        }, status=status.HTTP_201_CREATED)
