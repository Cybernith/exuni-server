from rest_framework import status
from rest_framework.views import exception_handler

import logging

from helpers.bale import Bale

labels = {
    # Admin
    'company_name': 'نام شرکت',
    'business_type': 'نوع کسب و کار',
    'sale_date': 'تاریخ فروش',
    'selling_type': 'نوع فروش',

    # User
    'username': 'نام کاربری',
    'confirmation_code': 'کد تایید',

    # Use full
    'name': 'نام',
    'postal_code': 'کد پستی',
    'mobile': 'موبایل',
    'phone': 'موبایل',
    'account': 'حساب',
    'bedAccount': 'حساب',
    'besAccount': 'حساب',
    'date': 'تاریخ',
    'type': 'نوع',

    # Company & Financial Year
    'warehouse_system': 'سیستم انبار',
    'financialYears': 'سال های مالی',

    # Cheque
    'serial_from': 'از شماره سریال',
    'serial_to': 'تا شماره سریال',

    # Ware
    'ware': 'کالا',
    'unit': 'واحد شمارش',
    'category': 'دسته بندی',
    'pricingType': 'نوع قیمت گذاری',
    'price': 'قیمت',
    'warehouse': 'انبار',

    # Factor
    'handler': 'انبار گردان',

    # Other
    'code': 'شماره',
    'form': 'فرم',
    'post': 'سمت',
    'percent': 'درصد',
    'user': 'کاربر',
    'explanation': 'توضیحات',

    # Dashtbashi
    'destination': 'مقصد',
    'origin': 'مبدا',
    'contractor': 'پیمانکار',
    'end_date': 'تاریخ پایان',
    'loading_date': 'تاریخ بارگیری',
    'issue_date': 'تاریخ صدور',
    'remittance_payment_method': 'روش پرداخت مبلغ حواله',
    'driver_tip_payer': 'پرداخت کننده انعام',
    'lading_number': 'شماره بارگیری',
    'billNumber': 'شماره بارنامه',
    'receive_type': 'نحوه دریافت',
    'owner': 'مالک',
    'bill_price': 'مبلغ بارنامه',
    'driving': 'حمل کننده',
    'month': 'ماه',
    'lading_bill_difference_receiver': 'دریافت کننده اختلاف بارنامه',

    #payroll
    'company': 'شرکت',
    'employer_name': 'نام کارفرما',
    'workshop': 'کارگاه',
    'episode': 'tedad mah'
}


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    if response is not None and response.status_code != status.HTTP_500_INTERNAL_SERVER_ERROR:
        errors = []
        data = response.data
        if isinstance(data, list):
            message = data[0]
        else:
            message = data.get('detail')

        if not message:
            for field, value in response.data.items():
                errors.append({
                    'field': labels.get(field, field),
                    'messages': value
                })
        else:
            if isinstance(message, dict) and 'non_field_errors' in message:
                errors.append({
                    'field': 'non_field_errors',
                    'messages': message['non_field_errors']
                })
            else:
                errors.append({
                    'field': '',
                    'messages': [message]
                })

        response.data = errors

    return response


class BaleLogHandler(logging.Handler):

    def emit(self, record):
        text = self.format(record)
        print(text)
        Bale.to_me(text)
