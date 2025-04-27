import pyotp
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from axes.attempts import is_already_locked

from helpers.functions import get_lockout_remaining_time


class SecretKeyView(APIView):
    permission_classes = (IsAuthenticated,)

    @staticmethod
    def verify(secret_key, code):
        totp = pyotp.TOTP(secret_key)

        is_verified = totp.verify(code)
        if is_verified:
            return True
        else:
            raise ValidationError("کد اشتباه است")

    def get(self, request):
        secret_key = pyotp.random_base32()
        return Response({
            'secret_key': secret_key,
            'qr_code': pyotp.totp.TOTP(secret_key).provisioning_uri(name=request.user.username, issuer_name="اکسونی")
        })

    def put(self, request):
        data = self.request.data
        secret_key = data.get('secret_key', '')
        code = data.get('code', '')

        user = request.user

        if self.verify(secret_key, code):
            user.secret_key = request.data.get('secret_key')
            user.save()

        return Response([])

    def delete(self, request):
        user = request.user
        code = request.data.get('code', '')
        if self.verify(user.secret_key, code):
            user.secret_key = None
            user.save()

        return Response([])


class ObtainAuthTokenView(ObtainAuthToken):

    def post(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        if user.username and is_already_locked(request, credentials={'username': user.username}):
            message = f" اکانت شما به دلیل تلاش‌های ناموفق قفل شده است. لطفاً بعد از {get_lockout_remaining_time(user.username)} دوباره امتحان کنید"
            return Response(
                {'detail': message},
                status=status.HTTP_423_LOCKED
            )

        if user.secret_key:
            code = request.data.get('code', None)
            if code:
                SecretKeyView.verify(user.secret_key, code)
            else:
                return Response({'need_two_factor_authentication': True})

        Token.objects.filter(user=user).delete()
        token, created = Token.objects.get_or_create(user=user)

        return Response({
            'need_two_factor_authentication': False,
            'token': token.key,
        })
