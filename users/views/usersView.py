from django.contrib.auth import authenticate
from django.db.models import QuerySet
from django.http import Http404
from rest_framework import status, generics
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from helpers.auth import BasicCRUDPermission
from helpers.functions import get_current_user
from helpers.models import manage_files
from helpers.views.recaptcha import RecaptchaView
from users.models import User, PhoneVerification
from users.serializers import UserListSerializer, UserCreateSerializer, UserUpdateSerializer, \
     UserRetrieveSerializer, UserNotificationSerializer, CurrentUserNotificationSerializer
from rest_framework.parsers import MultiPartParser, FormParser


class CurrentUserApiView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        return Response(UserRetrieveSerializer(request.user).data)


class CurrentUserNotificationApiView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        return Response(CurrentUserNotificationSerializer(request.user).data)


class UserListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, BasicCRUDPermission)
    permission_basename = 'user'
    serializer_class = UserListSerializer

    def get_queryset(self) -> QuerySet:
        return User.objects.hasAccess('get').filter(
            companyUsers__company=self.request.user.active_company
        )


class UserCreateView(generics.CreateAPIView):
    serializer_class = UserCreateSerializer

    def get_queryset(self) -> QuerySet:
        return User.objects.all()


class UserUpdateView(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    permission_basename = 'user'
    serializer_class = UserUpdateSerializer
    parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self) -> QuerySet:
        return User.objects.filter(pk=self.request.user.id)

    def perform_update(self, serializer: UserUpdateSerializer) -> None:
        manage_files(serializer.instance, self.request.data, ['profile_picture'])
        serializer.save()


class SendVerificationCodeView(APIView, RecaptchaView):
    throttle_scope = 'verification_code'

    def post(self, request):
        data = request.data
        username = data.get('username')

        if not self.request.user:
            self.verify_recaptcha()
        phone = PhoneVerification.send_verification_code(username=username, phone=data.get('phone'))

        if phone is not None:
            phone_sample = phone[8:] + " **** " + phone[:4]
            return Response(data={'phone_sample': phone_sample}, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)


class SendVerificationCodeForRegisterView(APIView, RecaptchaView):
    throttle_scope = 'verification_code'

    def post(self, request):
        data = request.data
        username = data.get('username')

        if not self.request.user:
            self.verify_recaptcha()

        if User.objects.filter(username=username).exists():
            raise ValidationError('کد ملی قبلا در سامانه ثبت شده است')
        else:
            phone = PhoneVerification.send_verification_code(username=None, phone=data.get('phone'))

            if phone is not None:

                phone_sample = phone[8:] + " **** " + phone[:4]

                return Response(data={'phone_sample': phone_sample}, status=status.HTTP_200_OK)

            else:

                return Response(status=status.HTTP_404_NOT_FOUND)


class CheckVerificationCodeView(APIView, RecaptchaView):
    throttle_scope = 'verification_code'

    def post(self, request):
        self.verify_recaptcha()

        data = request.data

        username = data['username']
        verificationCode = data.get('verificationCode')
        verificationCode = PhoneVerification.check_verification_code(username=username, phone=None,
                                                                     code=verificationCode, raise_exception=True)

        if verificationCode is not None:
            return Response(data={'verificationCode': verificationCode}, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)


class CheckVerificationForRegister(APIView, RecaptchaView):
    throttle_scope = 'verification_code'

    def post(self, request):
        self.verify_recaptcha()

        data = request.data

        username = data['username']
        if User.objects.filter(username=username).exists():
            raise ValidationError('کد ملی در سامانه تکراری میباشد')

        verification_code = data.get('verification_code')
        phone = data.get('phone')
        verification_code = PhoneVerification.check_verification_code(username=None, phone=phone,
                                                                      code=verification_code,
                                                                      raise_exception=True)

        if verification_code:
            return Response(data={'verificationCode': verification_code}, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)


class ChangePhoneView(APIView, RecaptchaView):
    throttle_scope = 'verification_code'

    def post(self, request):
        self.verify_recaptcha()

        data = request.data
        username = data['username']
        verification_code = data.get('verificationCode')
        new_phone = data.get('new_phone')
        verification_code = PhoneVerification.check_verification_code(username=None, phone=new_phone,
                                                                      code=verification_code,
                                                                      raise_exception=True)

        if verification_code is not None:
            user = User.objects.get(username=username)
            user.phone = new_phone
            user.save()
            return Response(data={'verificationCode': verification_code}, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)


class ChangePasswordView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        data = request.data
        user = authenticate(request, username=request.user.username, password=data.get('old_password'))
        if user:
            user.set_password(request.data.get('new_password'))
            user.save()
        else:
            return Response(["مشخصات وارد شده اشتباه می باشد"], status=status.HTTP_400_BAD_REQUEST)

        return Response([])


class ChangePasswordByVerificationCodeView(APIView, RecaptchaView):

    def post(self, request):
        self.verify_recaptcha()

        data = request.data
        username = data.get('username')
        new_password = data.get('new_password')
        verification_code = data.get('code')
        try:
            user = get_object_or_404(User, username=username)
            result = PhoneVerification.check_verification_code(username=username, phone=None, code=verification_code,
                                                               raise_exception=True)

            if result == verification_code:
                user.set_password(new_password)
                user.save()
                return Response(status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_404_NOT_FOUND)
        except User.DoesNotExist:
            raise ValidationError('نام کاربری اشتباه می باشد')




class UserByUsernameSearch(APIView):
    permission_classes = (IsAuthenticated,)
    permission_basename = 'workshop'

    def get_object(self, username):
        try:
            return User.objects.hasAccess('get').get(username=username)
        except User.DoesNotExist:
            raise Http404

    def get(self, request, username):
        query = self.get_object(username)
        serializers = UserUpdateSerializer(query)
        return Response(serializers.data, status=status.HTTP_200_OK)
