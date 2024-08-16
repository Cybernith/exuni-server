import threading
from re import sub

from django.contrib.auth.middleware import get_user
from django.utils.functional import SimpleLazyObject
from rest_framework.authtoken.models import Token
from rest_framework_jwt.authentication import JSONWebTokenAuthentication


class ModifyRequestMiddleware:
    user = None
    thread_local = None

    def __init__(self, get_response, thread_local=threading.local()):
        self.get_response = get_response
        ModifyRequestMiddleware.thread_local = thread_local

    def __call__(self, request):
        return self.process_request(request)

    def process_request(self, request):
        user = SimpleLazyObject(lambda: self.get_actual_value(request))

        header_token = request.META.get('HTTP_AUTHORIZATION', None)
        if header_token:
            token = sub('Token ', '', request.META.get('HTTP_AUTHORIZATION', None))
        else:
            token = request.GET.get('token', None)

        try:
            token_obj = Token.objects.get(key=token)
            request.user = token_obj.user
        except Token.DoesNotExist:
            pass

        if user.is_authenticated:
            self.thread_local.user = user

        return self.get_response(request)

    @staticmethod
    def get_actual_value(request):
        if request.user is None:
            return None
        return request.user

    @staticmethod
    def get_jwt_user(request):
        user = get_user(request)
        if user.is_authenticated:
            return user
        jwt_authentication = JSONWebTokenAuthentication()
        if jwt_authentication.get_jwt_value(request):
            user, jwt = jwt_authentication.authenticate(request)
        return user
