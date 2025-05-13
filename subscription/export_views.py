import pandas
from django.db.models import Q
from io import BytesIO

from helpers.functions import add_separator, date_to_str, datetime_to_time
from reports.lists.export_views import BaseExportView
from subscription.models import Factor, Transaction
from subscription.views import FactorListView, UserTurnover
import xlsxwriter
from django.http import HttpResponse


class SubscriptionFactorListExportView(FactorListView, BaseExportView):
    template_name = 'export/sample_form_export.html'
    filename = 'factor'

    context = {
        'title': 'لیست فاکتور ها',
    }
    pagination_class = None

    def get_queryset(self):
        return self.filterset_class(self.request.GET, queryset=super().get_queryset()).qs

    def get(self, request, export_type, *args, **kwargs):
        return self.export(request, export_type, *args, **kwargs)

    def get_context_data(self, user, print_document=False, **kwargs):
        qs = self.get_queryset()
        context = {
            'forms': qs,
            'user': user,
            'print_document': print_document
        }

        template_prefix = self.get_template_prefix()
        context['form_content_template'] = 'export/subscription_factor_list.html'
        context['right_header_template'] = 'export/sample_head.html'

        context.update(self.context)

        return context

    def xlsx_response(self, request, *args, **kwargs):
        sheet_name = "{}.xlsx".format(self.filename)

        with BytesIO() as b:
            writer = pandas.ExcelWriter(b, engine='xlsxwriter')
            data = []

            bordered_rows = []
            data += self.get_xlsx_data(self.get_context_data(user=request.user)['forms'])
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

    @staticmethod
    def get_xlsx_data(factors: Factor):
        data = [
            [
                'لیست فاکتور ها'
            ],
            ['تاریخ', 'ساعت', 'شناسه یکتا', 'مبلغ', 'مبلغ تخفیف', 'مبلغ پس از تخفیف', 'مالیات ارزش افزوده',
             'مبلغ نهایی', 'وضعیت پرداخت']
        ]
        for form in factors:
            is_paid = 'نا موفق'
            if form.is_paid:
                is_paid = 'موفق'
            data.append([
                date_to_str(form.created_at),
                datetime_to_time(form.created_at),
                form.id,
                round(form.amount),
                round(form.discount_amount),
                round(form.after_discount_amount),
                round(form.value_added_tax),
                round(form.get_payable_amount()),
                is_paid,
            ])
        return data


class SubscriptionFactorDetailExportView(FactorListView, BaseExportView):
    template_name = 'export/sample_form_export.html'
    filename = 'factor'

    context = {
        'title': 'جزییات فاکتور',
    }
    pagination_class = None

    def get_queryset(self):
        return self.filterset_class(self.request.GET, queryset=super().get_queryset()).qs

    def get(self, request, export_type, *args, **kwargs):
        return self.export(request, export_type, *args, **kwargs)

    def get_context_data(self, user, print_document=False, **kwargs):
        qs = self.get_queryset()
        context = {
            'forms': qs.first(),
            'user': user,
            'print_document': print_document
        }

        template_prefix = self.get_template_prefix()
        context['form_content_template'] = 'export/factor_detail.html'.format(template_prefix)
        context['right_header_template'] = 'export/sample_head.html'

        context.update(self.context)

        return context

    def xlsx_response(self, request, *args, **kwargs):
        sheet_name = "{}.xlsx".format(self.filename)

        with BytesIO() as b:
            writer = pandas.ExcelWriter(b, engine='xlsxwriter')
            data = []

            bordered_rows = []
            data += self.get_xlsx_data(self.get_context_data(user=request.user)['forms'])
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


class UserTurnoverListExportView(UserTurnover, BaseExportView):
    template_name = 'export/sample_form_export.html'
    filename = 'factor'

    context = {
        'title': 'لیست  گردش حساب کاربر',
    }
    pagination_class = None

    def get_queryset(self):
        return self.filterset_class(self.request.GET, queryset=super().get_queryset()).qs

    def get(self, request, export_type, *args, **kwargs):
        return self.export(request, export_type, *args, **kwargs)

    def get_context_data(self, user, print_document=False, **kwargs):
        qs = self.get_queryset()
        context = {
            'forms': qs,
            'user': user,
            'print_document': print_document
        }

        template_prefix = self.get_template_prefix()
        context['form_content_template'] = 'export/subscription_transactions_list.html'.format(template_prefix)
        context['right_header_template'] = 'export/sample_head.html'

        context.update(self.context)

        return context

    def xlsx_response(self, request, *args, **kwargs):
        sheet_name = "{}.xlsx".format(self.filename)

        with BytesIO() as b:
            writer = pandas.ExcelWriter(b, engine='xlsxwriter')
            data = []

            bordered_rows = []
            data += self.get_xlsx_data(self.get_context_data(user=request.user)['forms'])
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

    @staticmethod
    def get_xlsx_data(transactions: Transaction):
        data = [
            [
                'گردش حساب کاربر'
            ],
            ['تاریخ ', 'ساعت', 'توضیحات', 'بدهکار', 'بستانکار', 'مانده', 'فاکتور']
        ]
        for form in transactions:
            if form.factor:
                factor = form.factor.id
            else:
                factor = '-'
            data.append([
                date_to_str(form.created_at),
                datetime_to_time(form.created_at),
                form.explanation,
                add_separator(form.bed),
                add_separator(form.bes),
                add_separator(form.cumulative_remain),
                factor,
            ])
        return data
