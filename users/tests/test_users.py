import random

from django.urls.base import reverse
from rest_framework import status

from helpers.test import MTestCase
from users.models import User


class UserTest(MTestCase):

    def test_create_user(self):
        user = UserTest.get_user()
        self.client.force_authenticate(user)

        response = self.client.post(reverse('create-user'), data={
            'username': 'mmd',
            'password': '1234',
            'first_name': 'mohammad',
            'last_name': 'mostafaee',
            'phone': '09307468674',
        })

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.client.logout()

    def test_update_user(self):
        user = UserTest.get_user()
        self.client.force_authenticate(user)

        response = self.client.put(reverse('update-user', args=[user.id]), data={
            'username': 'mmd',
            'password': '1234',
            'first_name': 'mohammad',
            'last_name': 'mostafaee',
            'phone': '09307468674',
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.logout()

    def test_delete_user(self):
        self.client.force_authenticate(UserTest.get_user())

        user = UserTest.create_user()

        response = self.client.delete(reverse('destroy-user', args=[user.id]))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.client.logout()

    def test_user_change_password(self):
        user = UserTest.get_user()
        self.client.force_authenticate(user)

        response = self.client.post(reverse('change-user-password'), data={
            'user': user.id,
            'password': 'newPass'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.logout()

    def test_list_users(self):
        user = UserTest.get_user()
        self.client.force_authenticate(user)

        for i in range(3):
            UserTest.create_user()

        for i in range(1):
            UserTest.create_user(superuser=user)

        response = self.client.get(reverse('list-users'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        self.client.logout()

    def test_retrieve_user(self):
        user = UserTest.get_user()
        self.client.force_authenticate(user)

        response = self.client.get(reverse('current-user'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.logout()

    def test_set_active_company(self):
        user = UserTest.get_user()
        self.client.force_authenticate(user)

        from companies.tests.test_companies import CompanyTest
        company = CompanyTest.create_company(user)

        response = self.client.post(reverse('set-active-company'), data={
            'company': company.id
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(user.active_company.id, company.id)

        self.client.logout()

    def test_set_active_financial_year(self):
        # todo: fill this function
        pass

    @staticmethod
    def get_user():
        from companies.models import Company

        user = User.objects.filter(is_superuser=True).first()
        user.max_users = 100
        user.max_companies = 100

        if not user.active_company:
            company = Company.objects.first()
            financial_year = company.financial_years.first()
            user.active_company = company
            user.active_financial_year = financial_year

        user.save()

        return user

    @staticmethod
    def create_user(username=None, password=None, phone=None, superuser=None):
        user = User.objects.create(
            username=username or "{} - {}".format(MTestCase.faker.name(), random.random()),
            phone=phone or MTestCase.get_fake_phone_number(),
            first_name=MTestCase.faker.name(),
            last_name=MTestCase.faker.name(),
            superuser=superuser,
        )
        user.set_password(password or MTestCase.faker.name())
        user.save()
        return user
