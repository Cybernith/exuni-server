import json
from datetime import datetime
from decimal import Decimal

from bson import Decimal128
from django.core.handlers.wsgi import WSGIRequest
from rest_framework.response import Response

from server.settings import RequestLogs


def serialize_data(dict_item):
    if dict_item is None: return None

    if not isinstance(dict_item, dict):
        return dict_item

    for k, v in list(dict_item.items()):
        if isinstance(v, dict):
            serialize_data(v)
        elif isinstance(v, list):
            for l in v:
                serialize_data(l)
        elif isinstance(v, Decimal):
            del dict_item[k]
            dict_item[str(k)] = Decimal128(str(v))
        else:
            del dict_item[k]
            dict_item[str(k)] = v

    return dict_item


class LogRequestMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: WSGIRequest):
        log = {'timestamp': datetime.utcnow().timestamp(), 'path': request.path, 'method': request.method.lower(), 'params': request.GET}

        user = request.user
        if user:
            log['user'] = {
                'id': user.id,
                'username': user.username
            }
        #
        # active_company = getattr(user, 'active_company', None)
        # if active_company:
        #     log['company'] = {
        #         'id': active_company.id,
        #         'name': active_company.name
        #     }
        #
        # active_financial_year = getattr(user, 'active_financial_year', None)
        # if active_financial_year:
        #     log['financial_year'] = {
        #         'id': active_financial_year.id,
        #         'name': active_financial_year.name
        #     }

        # body = getattr(request, 'body', {})
        # try:
        #     log['body'] = json.loads(serialize_data(body))
        # except:
        #     log['body'] = f'Error on decoding body:\n{request.body}'

        response: Response = self.get_response(request)

        log['status'] = response.status_code
        # log['response'] = serialize_data(response.data) if hasattr(response, 'data') else {}

        # if self.can_insert_log(log):
        #     RequestLogs.insert_one(log)

        return response

    @staticmethod
    def can_insert_log(log):
        exclusions = [
            log['path'] == '/test',  # test api
            log['method'] == 'get' and log['status'] == 200,  # get requests (like report and etc) with successful responses
        ]

        for condition in exclusions:
            if condition:
                return False

        return True
