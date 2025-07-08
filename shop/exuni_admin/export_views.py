import pandas
from django.db.models import Q
from io import BytesIO

from helpers.functions import add_separator, date_to_str, datetime_to_time, datetime_to_str, get_current_user
from reports.lists.export_views import BaseExportView
import xlsxwriter
from django.http import HttpResponse

from shop.exuni_admin.views import AdminShopOrderListView, AdminProcessingShopOrderListView, AdminPaidShopOrderListView

from shop.models import ShopOrder


class ShopOrderListExportView(AdminShopOrderListView, BaseExportView):
    template_name = 'export/sample_form_export.html'
    filename = 'orders'

    context = {
        'title': ' سفارش ها',
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
        context['form_content_template'] = 'export/shop_order_detail_list.html'
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
    def get_xlsx_data(orders: ShopOrder):
        data = [
            [
                'لیست سفارش ها'
            ],
            ['تاریخ ثبت', 'وضعیت', 'نام مشتری', 'شمار تماس مشتری', 'مبلغ', 'مبلغ تخفیف', 'مبلغ پس از تخفیف', 'تعداد اقلام', 'شناسه']
        ]
        for form in orders:
            data.append([
                datetime_to_str(form.date_time),
                form.get_status_display(),
                form.customer.name,
                form.customer.mobile_number,
                round(form.total_price),
                round(form.discount_amount),
                round(form.payable_amount),
                form.total_product_quantity,
                form.exuni_tracking_code,
            ])
        return data


class ShopOrderDetailExportView(AdminShopOrderListView, BaseExportView):
    template_name = 'export/sample_form_export.html'
    filename = 'ShopOrder'

    context = {
        'title': 'سفارش',
    }
    pagination_class = None

    def get_queryset(self):
        return self.filterset_class(self.request.GET, queryset=super().get_queryset()).qs

    def get(self, request, export_type, *args, **kwargs):
        return self.export(request, export_type, *args, **kwargs)

    def get_context_data(self, user, print_document=False, **kwargs):
        qs = self.get_queryset()
        context = {
            'forms': qs.filter(status='pr'),
            'user': user,
            'print_document': print_document
        }

        template_prefix = self.get_template_prefix()
        context['form_content_template'] = 'export/shop_order_detail.html'.format(template_prefix)
        context['right_header_template'] = 'export/sample_head.html'

        context.update(self.context)

        return context


class OrderPostDetailExportView(AdminShopOrderListView, BaseExportView):
    template_name = 'export/sample_form_export.html'
    filename = 'post'

    context = {
        'title': 'پست',
    }
    pagination_class = None

    def get_queryset(self):
        return self.filterset_class(self.request.GET, queryset=super().get_queryset()).qs

    def get(self, request, export_type, *args, **kwargs):
        return self.export(request, export_type, *args, **kwargs)

    def get_context_data(self, user, print_document=False, **kwargs):
        qs = self.get_queryset()
        context = {
            'forms': qs.filter(status='pr'),
            'user': user,
            'print_document': print_document
        }

        template_prefix = self.get_template_prefix()
        context['form_content_template'] = 'export/order_post_details.html'.format(template_prefix)
        context['right_header_template'] = 'export/sample_head.html'

        context.update(self.context)

        return context


class AdminOrdersListExportView(AdminShopOrderListView, BaseExportView):
    template_name = 'export/sample_form_export.html'
    filename = 'admin_orders'

    context = {
        'title': 'سفارش ها',
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
        context['form_content_template'] = 'export/shop_order_detail_list.html'.format(template_prefix)
        context['right_header_template'] = 'export/sample_head.html'

        context.update(self.context)

        return context


class AdminShippedOrdersListExportView(AdminShopOrderListView, BaseExportView):
    template_name = 'export/sample_form_export.html'
    filename = 'shipments'

    context = {
        'title': 'ارسال ها',
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
        context['form_content_template'] = 'export/shipped_orders_list.html'.format(template_prefix)
        context['right_header_template'] = 'export/sample_head.html'

        context.update(self.context)

        return context


class AdminOrdersExportView(AdminPaidShopOrderListView, BaseExportView):
    template_name = 'export/sample_form_export.html'
    filename = 'admin_orders'

    context = {
        'title': 'سفارش ها',
    }
    pagination_class = None

    def get_queryset(self):
        qs = self.filterset_class(self.request.GET, queryset=super().get_queryset()).qs
        qs.update(print_by=get_current_user(), is_printed=True)
        return qs

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
        context['form_content_template'] = 'export/admin_orders.html'.format(template_prefix)
        context['right_header_template'] = 'export/sample_head.html'

        context.update(self.context)

        return context


class AdminAllOrdersExportView(AdminShopOrderListView, BaseExportView):
    template_name = 'export/sample_form_export.html'
    filename = 'admin_orders'

    context = {
        'title': 'سفارش ها',
    }
    pagination_class = None

    def get_queryset(self):
        qs = self.filterset_class(self.request.GET, queryset=super().get_queryset()).qs
        qs.update(print_by=get_current_user(), is_printed=True)
        return qs

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
        context['form_content_template'] = 'export/admin_orders.html'.format(template_prefix)
        context['right_header_template'] = 'export/sample_head.html'

        context.update(self.context)

        return context


