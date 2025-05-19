from django import template

from helpers.functions import add_separator, rgetattr, date_to_str, fee_display, datetime_to_str
from server.settings import DATE_FORMAT, TIME_FORMAT
import datetime

register = template.Library()

@register.filter(is_safe=True)
def absoluteValue(value):
    return abs(value)


@register.filter(is_safe=True)
def minusRTL(value):
    if value and value < 0:
        return str(add_separator(value * -1)) + ' -'
    elif value and value >= 0:
        return add_separator(value)
    else:
        return 0

@register.filter(is_safe=True)
def toIntiger(value):
    if value:
        return int(value)
    else:
        return 0


@register.filter(is_safe=True)
def chequeStatuses(value):
    displays = {
        "blank": "سفید",
        "notPassed": "پاس نشده",
        "inFlow": "در جریان",
        "passed": "پاس شده",
        "bounced": "برگشتی",
        "cashed": "نقدی",
        "revoked": "باطل شده",
        "transferred": "انتقالی",
        "guarantee": "ضمانتی",
        "extended": "تمدید شده",
    }
    if value:
        return displays[value]
    else:
        return '-'


@register.filter(is_safe=True)
def roundMoney(value):
    if value:
        return add_separator(int(value))
    else:
        return 0

@register.filter(is_safe=True)
def roundToTowDigits(value):
    if value:
        if int(value) == round(value, 2):
            return int(value)
        else:
            return round(value, 2)
    else:
        return ''

@register.filter(is_safe=True)
def money(value):
    return add_separator(value)

@register.filter(is_safe=True)
def reverse_list(value):
    return value.reverse()


@register.filter(is_safe=True)
def jDate(value):
    if value:
        try:
            return date_to_str(value)
        except:
            return value
    return ''

@register.filter(is_safe=True)
def jDateTime(value):
    if value:
        try:
            return datetime_to_str(value)
        except:
            return value
    return ''


@register.filter(is_safe=True)
def dateToTime(value):
    if value:
        try:
            return value.strftime(TIME_FORMAT)
        except:
            return value
    return ''


@register.simple_tag
def colspan(initial_count, *args):
    count = initial_count
    for arg in args:
        if arg:
            count += 1
    return count



@register.simple_tag
def get_value(obj, key, headers):
    if isinstance(obj, list):
        value = obj[key]
    else:
        value_display = rgetattr(obj, 'get_{}_display'.format(key), None)
        if value_display:
            value = value_display()
        else:
            value = rgetattr(obj, key)

    if value is None:
        return '-'

    header = [header for header in headers if header['value'] == key][0]
    value_type = header.get('type', None)

    if value_type == 'numeric':
        return add_separator(value)
    if value_type == 'date':
        return date_to_str(value)
    elif value_type == 'select':
        return [item['text'] for item in header['items'] if item['value'] == value][0]
    elif value_type == 'boolean':
        return '&#10004;' if value else '&#10006;'
    elif value_type == 'fee':
        return fee_display(value)

    return value


@register.simple_tag
def get_ordered_items(obj):
    return obj.items.order_by('product__shelf_code')


@register.simple_tag
def today():
    return date_to_str(datetime.date.today())
