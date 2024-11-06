import datetime
import functools
from decimal import Decimal
from typing import Type

import jdatetime
from django.db.models.base import Model
from django.db.models.query_utils import Q

from server.settings import TESTING, DATE_FORMAT, DATETIME_FORMAT, TIME_FORMAT


def get_current_user():
    from helpers.middlewares.modify_request_middleware import ModifyRequestMiddleware
    if TESTING:
        user = getattr(ModifyRequestMiddleware, 'user', None)
    else:
        user = getattr(ModifyRequestMiddleware.thread_local, 'user', None)
    return user


def get_new_child_code(parent_code, child_code_length, last_child_code=None):
    if last_child_code:
        last_code = int(last_child_code) + 1
        code = str(last_code)
    else:
        last_code = '1'.zfill(child_code_length)
        code = parent_code + last_code

    if code[:len(parent_code)] != parent_code:
        from rest_framework import serializers
        raise serializers.ValidationError("تعداد فرزندان این سطح پر شده است")

    return code


def get_new_code(model: Type[Model], max_length=None):
    last_item = model.objects.inFinancialYear().filter(~Q(code=None)).order_by('-code').first()
    if last_item:
        code = last_item.code + 1
    else:
        code = 1

    if max_length and len(str(code)) > max_length:
        from rest_framework import serializers
        raise serializers.ValidationError("تعداد اعضای این سطح پر شده است")

    return code


def get_object_by_code(queryset, position, object_id=None):
    try:
        item = None
        if position == 'next' and object_id:
            item = queryset.filter(pk__gt=object_id).order_by('id')[0]
        elif position == 'prev' and object_id:
            if object_id:
                queryset = queryset.filter(pk__lt=object_id)
            item = queryset.order_by('-id')[0]
        elif position == 'first':
            item = queryset.order_by('id')[0]
        elif position == 'last':
            item = queryset.order_by('-id')[0]
        return item
    except IndexError:
        return None


def float_to_str(f):
    float_string = repr(float(f))
    if 'e' in float_string:  # detect scientific notation
        digits, exp = float_string.split('e')
        digits = digits.replace('.', '').replace('-', '')
        exp = int(exp)
        zero_padding = '0' * (abs(int(exp)) - 1)  # minus 1 for decimal point in the sci notation
        sign = '-' if f < 0 else ''
        if exp > 0:
            float_string = '{}{}{}.0'.format(sign, digits, zero_padding)
        else:
            float_string = '{}0.{}{}'.format(sign, zero_padding, digits)
    return add_separator(float_string.strip('0').strip('.'))


def add_separator(value):
    if value is None:
        return ''
    elif value == 0:
        return '0'
    try:
        str_value = '{:,}'.format(float(value))
    except ValueError:
        return value

    # str_value = str_value.replace(',', '/')

    if not str_value:
        str_value = '0'

    if str_value.endswith('.0'):
        str_value = str_value[:-2]

    return str_value


def get_dict_accounts(dic):
    return {
        'account': dic.get('account', None),
        'floatAccount1': dic.get('floatAccount1', None),
        'floatAccount2': dic.get('floatAccount2', None),
        'floatAccount3': dic.get('floatAccount3', None),
        'floatAccount4': dic.get('floatAccount4', None)
    }


def get_object_accounts(obj):
    return {
        'account': obj.account,
        'floatAccount1': obj.floatAccount1,
        'floatAccount2': obj.floatAccount2,
        'floatAccount3': obj.floatAccount3,
        'floatAccount4': obj.floatAccount4
    }


def get_object_accounts_ids(obj):
    return {
        'account': obj.account_id,
        'floatAccount1': obj.floatAccount1_id,
        'floatAccount2': obj.floatAccount2_id,
        'floatAccount3': obj.floatAccount3_id,
        'floatAccount4': obj.floatAccount4_id
    }


def get_object_account_names(obj):
    arr = [obj.account.name]
    if hasattr(obj, 'floatAccount1') and obj.floatAccount1: arr.append(obj.floatAccount1.name)
    if hasattr(obj, 'floatAccount2') and obj.floatAccount2: arr.append(obj.floatAccount2.name)
    if hasattr(obj, 'floatAccount3') and obj.floatAccount3: arr.append(obj.floatAccount3.name)
    if hasattr(obj, 'floatAccount4') and obj.floatAccount4: arr.append(obj.floatAccount4.name)
    return " - ".join(arr)


def date_to_str(value: datetime.date):
    if value:
        try:
            return jdatetime.date.fromgregorian(date=value).strftime(DATE_FORMAT)
        except ValueError:
            return str(value)
    else:
        return ''


def datetime_to_time(value: datetime.datetime):
    if value:
        try:
            return value.strftime(TIME_FORMAT)
        except ValueError:
            return str(value)
    else:
        return ''


def date_to_jalali(value: datetime.date):
    if value:
        try:
            return jdatetime.date.fromgregorian(date=value)
        except ValueError:
            return value
    else:
        return ''


def datetime_to_str(value: datetime.datetime):
    return jdatetime.datetime.fromgregorian(datetime=value).strftime(DATETIME_FORMAT)


def sanad_exp(*args):
    result = ""
    for arg in args:
        if isinstance(arg, datetime.date):
            arg = date_to_str(arg)
        elif isinstance(arg, Decimal):
            arg = str(arg).rstrip('0').rstrip('.')
        elif arg is None:
            arg = ' - '
        elif isinstance(arg, tuple):
            if arg[1]:
                arg = sanad_exp(*arg)
            else:
                continue
        else:
            arg = str(arg)

        result += arg
        if len(result) and result[-1] != " ":
            result += " "

    return result[:-1]


def rgetattr(obj, attr, *args):
    def _getattr(obj, attr):
        if isinstance(obj, dict):
            return obj.get(attr, None)
        else:
            if hasattr(obj, attr):
                return getattr(obj, attr, *args)
            else:
                return None

    return functools.reduce(_getattr, [obj] + attr.split('.'))


def to_gregorian(date):
    date = datetime.date(*list(map(int, date.split('-'))))
    return date.isoformat()


def get_label(choices, key):
    return [t[1] for t in choices if t[0] == key][0]


def get_key(choices, label):
    return [t[0] for t in choices if t[1] == label][0]


def bool_to_str(value: bool):  # check mark or cross in xlsx output
    if value == True:  # 'True' was explicitly written to avoid evaluating values of types other than bool
        return '✔'
    elif value == False:  # 'False' was explicitly written to avoid evaluating None types
        return '✖'

def is_valid_economic_code(input_code):
    code = str(input_code)
    status = True
    message = 'کد اقتصادی تایید شد'
    if len(code) != 12:
        status = False
        message = "کد اقتصادی باید ۱۲ رقم باشد"

    return status, message


def fee_display(value, display_type='html'):
    if isinstance(value, str):
        return value
    elif isinstance(value, float):
        return add_separator(value)
    elif isinstance(value, list):
        result = ''
        if len(value) == 1:
            result = add_separator(round(value[0]['fee']))
        else:
            for item in value:
                result += add_separator(round(item['fee']))
                if display_type == 'xlsx':
                    result += ' x '
                else:
                    result += '&#10006;'

                result += add_separator(round(item['count']))
                result += ' '

        return result

def get_financial_year_years():
    years = []
    financial_year = get_current_user().active_financial_year
    start = date_to_jalali(financial_year.start)
    end = date_to_jalali(financial_year.end)
    if start.year == end.year:
        years.append(start.year)
    else:
        counter = end.year - start.year
        while counter >= 0:
            years.append(start.year + counter)
            counter -= 1
    return sorted(years)


def get_financial_year_months(to_now=True):
    results = []
    start = date_to_jalali(get_current_user().active_financial_year.start).year
    end = date_to_jalali(get_current_user().active_financial_year.end).year
    start_month = date_to_jalali(get_current_user().active_financial_year.start).month
    end_month = date_to_jalali(get_current_user().active_financial_year.end).month

    months = [
        {'name': ' فروردین', 'value': '01', 'id': 1},
        {'name': ' اردیبهشت', 'value': '02', 'id': 2},
        {'name': ' خرداد', 'value': '03', 'id': 3},
        {'name': ' تیر', 'value': '04', 'id': 4},
        {'name': ' مرداد', 'value': '05', 'id': 5},
        {'name': ' شهریور', 'value': '06', 'id': 6},
        {'name': ' مهر', 'value': '07', 'id': 7},
        {'name': ' آبان', 'value': '08', 'id': 8},
        {'name': ' آذر', 'value': '09', 'id': 9},
        {'name': ' دی', 'value': '10', 'id': 10},
        {'name': ' بهمن', 'value': '11', 'id': 11},
        {'name': ' اسفند', 'value': '12', 'id': 12},
    ]

    months_days = {
        1: 31,
        2: 31,
        3: 31,
        4: 31,
        5: 31,
        6: 31,
        7: 30,
        8: 30,
        9: 30,
        10: 30,
        11: 30,
        12: 29,
    }

    for year in get_financial_year_years():
        current_year_months = []
        if start == end:
            for month in months:
                if month['id'] >= start_month and month['id'] <= end_month:
                    current_year_months.append(month)
        elif not year == start and not year == end:
            current_year_months = months
        elif year == start and not year == end:
            for month in months:
                if month['id'] >= start_month:
                    current_year_months.append(month)
        elif not year == start and year == end:
            for month in months:
                if month['id'] <= end_month:
                    current_year_months.append(month)

        for month in current_year_months:
            current_month_start = jdatetime.date(year, month['id'], 1)
            current_month_end = jdatetime.date(year, month['id'], months_days[month['id']])
            results.append(
                {
                    'title': month['name'] + ' ' + str(year),
                    'start': current_month_start.togregorian(),
                    'end': current_month_end.togregorian()
                }
            )

    response = []
    if to_now:
        for result in results:
            if (result['start'].__le__(datetime.date.today())):
                response.append(result)

        return response
    else:
        return results



def change_to_num(val):
    if val:
        return round(val)
    else:
        return 0