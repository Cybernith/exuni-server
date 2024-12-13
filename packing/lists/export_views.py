from helpers.functions import get_current_user
from packing.lists.views import OrderPackageWithoutAdminListView, WaitingForPackingOrdersListView, \
    WaitingForShippingOrdersListView, AdminPackingReportListView, OrderPackageListView, \
    AffiliateAdminOrderPackagesReportListView
from packing.models import OrderPackage
from reports.lists.export_views import BaseExportView
import pandas
from io import BytesIO
import xlsxwriter

from django.http import HttpResponse
import os
import jdatetime
from numpy import unique


class OrderWithoutAdminExportView(OrderPackageWithoutAdminListView, BaseExportView):
    template_name = 'export/sample_form_export.html'
    filename = 'OrderWithoutAdmin'

    context = {
        'title': 'سفارش های در انتظار بسته بندی',
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
            'user_name': get_current_user().first_name + ' ' +  get_current_user().last_name,
            'print_document': print_document,
            'logo': '/media/images/artech-2.png'
        }

        context['form_content_template'] = 'export/order_without_admin.html'
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
    def get_xlsx_data(order_packages: OrderPackage):
        data = [
            [
                'سفارش های در انتظار بسته بندی'
            ],
            ['نام کسب و کار', 'نام مشتری', 'تلفن', 'آدرس', 'تعداد اقلام']
        ]
        for form in order_packages:
            data.append([
                form.business.name,
                form.customer_name,
                form.phone,
                form.address,
                form.products_quantity,
            ])
        return data


class AllOrdersWithoutAdminReportExportView(OrderPackageWithoutAdminListView, BaseExportView):
    template_name = 'export/all_orders_form_export.html'
    filename = 'AllOrdersWithoutAdmin'

    context = {
        'title': 'سفارش های در انتظار بسته بندی',
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
            'user_name': get_current_user().first_name + ' ' +  get_current_user().last_name,
            'print_document': print_document,
            'logo': qs.first().business.logo.url,
        }

        context['form_content_template'] = 'export/all_orders.html'
        context['right_header_template'] = 'export/sample_head.html'

        context.update(self.context)

        return context




class WaitingForPackingOrdersExportView(WaitingForPackingOrdersListView, BaseExportView):
    template_name = 'export/sample_form_export.html'
    filename = 'WaitingForPackingOrders'

    context = {
        'title': 'سفارش های بسته بندی نشده',
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
            'user_name': get_current_user().first_name + ' ' +  get_current_user().last_name,
            'print_document': print_document,
            'logo': '/media/images/artech-2.png'
        }

        context['form_content_template'] = 'export/order_without_admin.html'
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
    def get_xlsx_data(order_packages: OrderPackage):
        data = [
            [
                'سفارش های بسته بندی نشده'
            ],
            ['نام کسب و کار', 'نام مشتری', 'تلفن', 'آدرس', 'تعداد اقلام']
        ]
        for form in order_packages:
            data.append([
                form.business.name,
                form.customer_name,
                form.phone,
                form.address,
                form.products_quantity,
            ])
        return data


class WaitingForPackingAllOrdersReportExportView(WaitingForPackingOrdersListView, BaseExportView):
    template_name = 'export/all_orders_form_export.html'
    filename = 'WaitingForPackingOrders'

    context = {
        'title': 'سفارش های در انتظار بسته بندی',
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
            'user_name': get_current_user().first_name + ' ' +  get_current_user().last_name,
            'print_document': print_document,
            'logo': qs.first().business.logo.url,
        }

        context['form_content_template'] = 'export/all_orders.html'
        context['right_header_template'] = 'export/sample_head.html'

        context.update(self.context)

        return context



class WaitingForShippingOrdersExportView(WaitingForShippingOrdersListView, BaseExportView):
    template_name = 'export/sample_form_export.html'
    filename = 'WaitingForShippingOrders'

    context = {
        'title': 'سفارش های پست  نشده',
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
            'user_name': get_current_user().first_name + ' ' +  get_current_user().last_name,
            'print_document': print_document,
            'logo': '/media/images/artech-2.png'
        }

        context['form_content_template'] = 'export/waiting_for_shipping.html'
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
    def get_xlsx_data(order_packages: OrderPackage):
        data = [
            [
                'سفارش های پست  نشده'
            ],
            ['نام کسب و کار', 'نام مشتری', 'تلفن', 'آدرس', 'تعداد اقلام', 'زمان بسته بندی']
        ]
        for form in order_packages:
            data.append([
                form.business.name,
                form.customer_name,
                form.phone,
                form.address,
                form.products_quantity,
                form.packing_data_time,
            ])
        return data


class WaitingForShippingAllOrdersReportExportView(WaitingForShippingOrdersListView, BaseExportView):
    template_name = 'export/all_orders_form_export.html'
    filename = 'WaitingForShippingAllOrders'

    context = {
        'title': 'سفارش های پست  نشده',
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
            'user_name': get_current_user().first_name + ' ' +  get_current_user().last_name,
            'print_document': print_document,
            'logo': qs.first().business.logo.url,
        }

        context['form_content_template'] = 'export/all_orders.html'
        context['right_header_template'] = 'export/sample_head.html'

        context.update(self.context)

        return context


class AdminPackingReportExportView(AdminPackingReportListView, BaseExportView):
    template_name = 'export/sample_form_export.html'
    filename = 'AdminPackingReport'

    context = {
        'title': 'گزارش بسته بندی های ادمین',
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
            'user_name': get_current_user().first_name + ' ' +  get_current_user().last_name,
            'print_document': print_document,
            'logo': '/media/images/artech-2.png'
        }

        context['form_content_template'] = 'export/admin_packing_report.html'
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
    def get_xlsx_data(order_packages: OrderPackage):
        data = [
            [
                'گزارش بسته بندی های ادمین'
            ],
            ['نام کسب و کار', 'نام مشتری', 'تلفن', 'آدرس', 'تعداد اقلام', 'زمان بسته بندی', 'زمان پست']
        ]
        for form in order_packages:
            data.append([
                form.business.name,
                form.customer_name,
                form.phone,
                form.address,
                form.products_quantity,
                form.packing_data_time,
                form.shipping_data_time,
            ])
        return data


class AdminPackingAllOrdersReportExportView(AdminPackingReportListView, BaseExportView):
    template_name = 'export/all_orders_form_export.html'
    filename = 'AdminPackingAllOrdersReport'

    context = {
        'title': 'گزارش بسته بندی های ادمین',
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
            'user_name': get_current_user().first_name + ' ' +  get_current_user().last_name,
            'print_document': print_document,
            'logo': qs.first().business.logo.url,
        }

        context['form_content_template'] = 'export/all_orders.html'
        context['right_header_template'] = 'export/sample_head.html'

        context.update(self.context)

        return context


class OrderPackageExportView(OrderPackageListView, BaseExportView):
    template_name = 'export/sample_order_export.html'
    filename = 'OrderPackage'

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
            'forms': qs,
            'form': qs.first(),
            'user_name': get_current_user().first_name + ' ' +  get_current_user().last_name,
            'print_document': print_document,
            'logo': qs.first().business.logo.url,
            'packed_date': qs.first().packing_data_time,
            'shipped_date': qs.first().shipping_data_time
        }

        context['form_content_template'] = 'export/order_package.html'
        context['right_header_template'] = 'export/sample_head.html'

        context.update(self.context)

        return context


class AffiliateAdminOrderPackagesReportExportView(AffiliateAdminOrderPackagesReportListView, BaseExportView):
    template_name = 'export/sample_form_export.html'
    filename = 'AdminPackingReport'

    context = {
        'title': 'گزارش  سفارشات',
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
            'user_name': get_current_user().first_name + ' ' +  get_current_user().last_name,
            'print_document': print_document,
            'logo': '/media/images/artech-2.png'
        }

        context['form_content_template'] = 'export/admin_packing_report.html'
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
    def get_xlsx_data(order_packages: OrderPackage):
        data = [
            [
                'گزارش  سفارشات'
            ],
            ['نام کسب و کار', 'نام مشتری', 'تلفن', 'آدرس', 'تعداد اقلام', 'زمان بسته بندی', 'زمان پست']
        ]
        for form in order_packages:
            data.append([
                form.business.name,
                form.customer_name,
                form.phone,
                form.address,
                form.products_quantity,
                form.packing_data_time,
                form.shipping_data_time,
            ])
        return data

