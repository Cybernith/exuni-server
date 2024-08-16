import datetime

from django.contrib.auth.models import AnonymousUser
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.renderers import JSONRenderer
from rest_framework.request import Request
from rest_framework.response import Response

from users.models import User


class CheckFinancialYearMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: Request):
        user = request.user

        if user and not isinstance(user, AnonymousUser) and request.method.lower() not in ('option', 'get') and request.is_ajax():
            financial_year = int(request.headers.get('financial-year', 0))
            active_financial_year_id = user.active_financial_year_id

            if active_financial_year_id and financial_year != active_financial_year_id:
                response = Response("سال مالی تغییر کرده است", status=status.HTTP_409_CONFLICT)
                response.accepted_renderer = JSONRenderer()
                response.accepted_media_type = "application/json"
                response.renderer_context = {}
                response.render()
                return response

        return self.get_response(request)
