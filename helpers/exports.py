from io import BytesIO
from typing import Any, Dict

import pandas
import xlsxwriter
from django.http.response import HttpResponse
from django.shortcuts import render
from wkhtmltopdf.views import PDFTemplateView


class MPDFTemplateView(PDFTemplateView):
    cmd_options = {
        'margin-top': 3,
        'footer-center': '[page]/[topage]'
    }

    context = None

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        if not self.context:
            raise NotImplementedError("Define context or implement get_context_data method")
        return self.context

    def render(self, request):
        return render(request, self.template_name, context=self.get_context_data(request=request))


def get_xlsx_response(file_name, data):
    with BytesIO() as b:
        writer = pandas.ExcelWriter(b, engine='xlsxwriter')

        if not file_name.endswith('.xlsx'):
            file_name = "{}.xlsx".format(file_name)

        sheet_name = 'Sheet1'

        df = pandas.DataFrame(data)
        df.to_excel(
            writer,
            sheet_name=sheet_name,
            index=False,
            header=False
        )
        workbook = writer.book
        worksheet = writer.sheets[sheet_name]
        worksheet.right_to_left()

        cell_format = writer.book.add_format({'num_format': '#,##0.00', 'align': 'center'})
        writer.sheets[sheet_name].set_column('B:Z', None, cell_format)

        border_fmt = workbook.add_format({'bottom': 1, 'top': 1, 'left': 1, 'right': 1})
        worksheet.conditional_format(xlsxwriter.utility.xl_range(
            0, 0, len(data) - 1, len(df.columns) - 1
        ), {'type': 'no_errors', 'format': border_fmt})
        writer.save()

        response = HttpResponse(b.getvalue(), content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(file_name)
        return response
