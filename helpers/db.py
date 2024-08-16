import gc
from abc import ABC

from django.db import connection, models
from django.db.models import Func


def bulk_create(model_class, model_array, chunk=50):
    for i in range(0, len(model_array), chunk):
        model_class.objects.bulk_create(model_array[i: i + chunk])


def queryset_iterator(queryset, chunk_size=100, key=None):
    if isinstance(queryset, list):
        return queryset

    key = [key] if isinstance(key, str) else (key or ['pk'])
    counter = 0
    count = chunk_size
    while count == chunk_size:
        offset = counter - counter % chunk_size
        count = 0
        for item in queryset.all().order_by(*key)[offset:offset + chunk_size]:
            count += 1
            yield item
        counter += count
        gc.collect()


class DateAdd(Func, ABC):
    """
    Custom Func expression to add date and int fields as day addition
    Usage: SubscriptionProduct.objects.annotate(end_date=DateAdd('start_date','duration')).filter(end_date__gt=datetime.now)
    """
    arg_joiner = " + CAST("
    template = "%(expressions)s || ' days' as INTERVAL)"
    output_field = models.DateField()


def select_raw_sql(sql):
    with connection.cursor() as cursor:
        cursor.execute(sql)

        columns = [col[0] for col in cursor.description]
        return [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]


def get_empty_array():
    return []
