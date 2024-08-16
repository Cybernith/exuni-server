import datetime
from rest_framework.authtoken.models import Token
from rest_framework.request import Request


class CheckTokenExpiration:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: Request):
        user = request.user

        if request.path != '/login' and user and user.pk and hasattr(user, 'auth_token'):
            now = datetime.datetime.now()

            token: Token = user.auth_token
            if token.created < now - datetime.timedelta(hours=1):
                token.delete()
            else:
                token.created = now
                token.save()

        return self.get_response(request)
