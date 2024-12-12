import datetime
import json
import re
from io import BytesIO

import jdatetime
import pandas
import xlsxwriter
from django.db.models import Q
from django.http.response import HttpResponse
from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from wkhtmltopdf.views import PDFTemplateView

from helpers.exports import get_xlsx_response
from helpers.functions import rgetattr, date_to_str, add_separator, bool_to_str, fee_display
from server.settings import DATE_FORMAT



class BaseExportView(APIView, PDFTemplateView):
    # filename = 'my_pdf'
    template_name = 'export/factor_export.html'

    cmd_options = {
        'margin-top': 3,
        'footer-center': '[page]/[topage]'
    }
    queryset = None
    filterset_class = None
    context = {}
    template_prefix = None

    def get_template_prefix(self):
        if self.template_prefix:
            return self.template_prefix
        return re.sub(r'(?<!^)(?=[A-Z])', '_', self.get_serializer().Meta.model.__name__).lower()

    def get_context_data(self, user, print_document=False, **kwargs):
        qs = self.get_queryset()

        context = {
            'forms': qs,
            'company': user.active_company,
            'financial_year': user.active_financial_year,
            'user': user,
            'name': CompanyUser.objects.filter(Q(user=user) & Q(company=user.active_company)).first().nickname,
            'print_document': print_document
        }

        template_prefix = self.get_template_prefix()
        context['form_content_template'] = 'export/{}_form_content.html'.format(template_prefix)
        context['right_header_template'] = 'export/{}_right_header.html'.format(template_prefix)

        context.update(self.context)

        return context

    def xlsx_response(self, request, *args, **kwargs):
        sheet_name = "{}.xlsx".format(self.filename)

        with BytesIO() as b:
            writer = pandas.ExcelWriter(b, engine='xlsxwriter')
            data = []

            bordered_rows = []
            i = 0
            for form in self.get_context_data(user=request.user)['forms']:
                data += self.get_xlsx_data(form)

                bordered_rows.append([i, len(data) - 1])

                i = len(data) + 2

                data.append([])
                data.append([])

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

            border_fmt = workbook.add_format({'bottom': 1, 'top': 1, 'left': 1, 'right': 1})

            for bordered_row in bordered_rows:
                worksheet.conditional_format(xlsxwriter.utility.xl_range(
                    bordered_row[0], 0, bordered_row[1], len(df.columns) - 1
                ), {'type': 'no_errors', 'format': border_fmt})
            writer.save()
            response = HttpResponse(b.getvalue(), content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename="{}"'.format(sheet_name)
            return response

    def pdf_response(self, request, *args, **kwargs):
        self.filename = "{}.pdf".format(self.filename)
        return super().get(request, user=request.user, *args, **kwargs)

    def print_response(self, request, *args, **kwargs):
        return render(
            request,
            self.template_name,
            context=self.get_context_data(user=request.user, print_document=True)
        )

    def export(self, request, export_type, *args, **kwargs):
        if export_type == 'xlsx':
            return self.xlsx_response(request, *args, **kwargs)
        elif export_type == 'pdf':
            return self.pdf_response(request, *args, **kwargs)
        else:
            return self.print_response(request, *args, **kwargs)


class BaseListExportView(PDFTemplateView):
    """
    Use this class after the list class, then override get method and call `get_response`
    """
    filename = None
    title = None
    context = {}
    filters = []
    right_header_template = None

    template_name = 'export/list_export.html'
    pagination_class = None

    def get_additional_data(self):
        """
        Data to put above the table in text, value format
        :return: array of {text: '...', value: '...'}
        """
        return []

    def get_applied_filters(self):
        applied_filters = self.request.GET.get('applied_filters', "[]")
        applied_filters = json.loads(applied_filters)
        return applied_filters

    def get_headers(self):
        headers = self.request.GET.get('headers', "[]")
        headers = json.loads(headers)
        return headers

    def get_header_texts(self):
        headers = self.get_headers()
        return ['#'] + [header['text'] for header in headers]

    def get_header_values(self):
        headers = self.get_headers()
        return [header['value'] for header in headers]

    def get_rows(self):
        return self.filterset_class(self.request.GET, queryset=self.get_queryset()).qs.all()

    def get_appended_rows(self):
        return []

    def get_right_header_template(self):
        return self.right_header_template

    def get_filters(self):
        filters = []
        data = self.request.GET.copy()
        data.pop('headers', None)
        data.pop('applied_filters', None)
        data.pop('token', None)
        headers = self.get_headers()
        keys = list(data.keys())
        keys.sort()
        for key in keys:

            text = [header['text'] for header in headers if header['value'].replace('.', '__') in key]
            if len(text):
                text = text[0]
            else:
                continue

            value = data[key]
            if key.endswith('gt') or key.endswith('gte'):
                text = "از {}".format(text)
            elif key.endswith('lt') or key.endswith('lte'):
                text = "تا {}".format(text)
            elif key.endswith('startswith'):
                text = "{} شروع شود با".format(text)
            elif key.endswith('icontains'):
                text = "{} دارا باشد".format(text)

            filters.append({
                'text': text,
                'value': value
            })

        filters = self.filters + filters

        return filters

    def get_context_data(self, user, print_document=False, **kwargs):
        context = {
            'company': user.active_company,
            'user': user,
            'title': self.title,
            'headers': self.get_header_texts(),
            'values': self.get_header_values(),
            'raw_headers': self.get_headers(),
            'rows': self.get_rows(),
            'appended_rows': self.get_appended_rows(),
            'applied_filters': self.get_applied_filters(),
            'print_document': print_document,
            'additional_data': self.get_additional_data(),
            'right_header_template': self.get_right_header_template(),
            'filters': []
        }

        context.update(self.context)

        return context

    def get_response(self, request, *args, **kwargs):
        export_type = kwargs.get('export_type')

        if export_type == 'xlsx':
            return get_xlsx_response('{}.xlsx'.format(self.filename), self.get_xlsx_data(self.get_rows()))
        elif export_type == 'pdf':
            self.filename = "{}.pdf".format(self.filename)
            return super().get(request, user=request.user, *args, **kwargs)
        else:
            return render(
                request,
                'export/list_export.html',
                context=self.get_context_data(user=request.user, print_document=True)
            )

    def get_xlsx_data(self, items):
        applied_filters = self.get_applied_filters()
        filters_text = ""
        for applied_filter in applied_filters:
            filters_text += applied_filter['text']
            type_text = applied_filter.get('typeText')
            if type_text:
                filters_text += " ({})".format(type_text)
            filters_text += ": {}  -  ".format(applied_filter['value'])

        data = [
            [self.title],
            ["فیلتر های اعمال شده:", filters_text],
            *[[data['text'], data['value']] for data in self.get_additional_data()],
            self.get_header_texts()
        ]
        i = 0
        for item in list(items) + self.get_appended_rows():
            i += 1
            row = [i]
            for header in self.get_headers():
                value = rgetattr(item, header['value'])
                value_type = header.get('type', None)

                if value_type == 'numeric':
                    value = add_separator(value)
                elif value_type == 'date' or isinstance(value, datetime.date):
                    value = date_to_str(value)
                elif value_type == 'boolean':
                    value = bool_to_str(value)
                elif value_type == 'text' and value is not None:
                    value = str(value)
                elif value_type == 'select' and value is not None:
                    value = [item['text'] for item in header['items'] if item['value'] == value][0]
                elif value_type == 'fee' and value is not None:
                    value = fee_display(value, display_type='xlsx')
                else:
                    value_display = rgetattr(item, 'get_{}_display'.format(header['value']), None)
                    if value_display:
                        value = value_display()

                row.append(value)
            data.append(row)

        return data


