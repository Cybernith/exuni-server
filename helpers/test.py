import datetime
from random import random
from typing import Optional, Any

import jdatetime
from django.core.exceptions import ValidationError
from django.db.models.base import Model
from faker import Faker
from rest_framework.test import APIClient, APITestCase

from helpers.middlewares.modify_request_middleware import ModifyRequestMiddleware
from helpers.validators import ModelValidator
from server.settings import TESTING


def set_user(user):
    if TESTING:
        ModifyRequestMiddleware.user = user
    else:
        ModifyRequestMiddleware.thread_local = type('thread_local', (object,), {
            'user': user
        })


class MAPIClient(APIClient):
    def force_authenticate(self, user: Optional[Model] = ..., token: Optional[Any] = ...) -> None:
        super(MAPIClient, self).force_authenticate(user, token)
        set_user(user)


class MTestCase(APITestCase):
    # fixtures = ['1-users.json', '2-companies.json', '3-accounts.json', '4-options.json', '5-wares.json']
    faker = Faker('fa_IR')

    def setUp(self):
        self.client = MAPIClient()
        return super().setUp()

    @staticmethod
    def get_fake_phone_number():
        while True:
            phone = '09' + str(int(random() * 10 ** 9))
            try:
                ModelValidator.phone_validator(phone)
                break
            except ValidationError:
                continue
        return phone

    @staticmethod
    def get_fake_jalali_date():
        date = datetime.datetime.strptime(MTestCase.faker.date(), "%Y-%m-%d")
        date = jdatetime.date.fromgregorian(date=date).strftime("%Y-%m-%d")
        return date
