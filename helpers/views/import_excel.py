from io import BytesIO
import pandas
from django.http import HttpResponse
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView


class ImportExcel(APIView):

    def get_rows(self):
        file_obj = self.request.FILES.get('file')
        if not file_obj:
            raise ValidationError("فایل انتخاب نشده است")
        df = pandas.read_excel(file_obj)
        df.where(df.notnull(), None)
        rows = df.to_dict('index')
        return rows

    @staticmethod
    def get_excel_response(sheet_name, data):
        file_name = f'{sheet_name}.xlsx'

        with BytesIO() as b:
            writer = pandas.ExcelWriter(b, engine='xlsxwriter')
            df = pandas.DataFrame(data)
            df.to_excel(
                writer,
                sheet_name=sheet_name,
                index=False,
                header=False
            )
            worksheet = writer.sheets[sheet_name]
            worksheet.right_to_left()
            writer.save()
            response = HttpResponse(b.getvalue(), content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename="{}"'.format(file_name)
            return response

    @staticmethod
    def get_field(i, row, field):
        value = row.get(field)
        if value:
            if pandas.isna(value):
                return None
            return value
        else:
            raise ValidationError("خطا در خواندن فایل (ردیف {}، ستون {})".format(i + 2, field))
