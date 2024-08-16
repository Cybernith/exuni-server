import random

from django.contrib.auth.models import Permission
from django.urls.base import reverse
from rest_framework import status

from helpers.test import MTestCase
from users.models import Role
from users.tests.test_users import UserTest


class RoleTest(MTestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = UserTest.get_user()

    def test_create_role(self):
        self.client.force_authenticate(self.user)

        permissions = Permission.objects.all().values_list('id', flat=True)

        response = self.client.post(reverse('create-role'), data={
            'name': 'accountant',
            'permissions': list(permissions)
        })

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = response.data
        self.assertEqual(len(data['permissions']), permissions.count())

        self.client.logout()

    def test_update_role(self):
        self.client.force_authenticate(self.user)

        role = self.create_role(self.user.active_company)

        response = self.client.put(reverse('update-role', args=[role.id]), data={
            'name': 'bikar',
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.logout()

    def test_delete_role(self):
        self.client.force_authenticate(self.user)

        role = self.create_role(self.user.active_company)

        response = self.client.delete(reverse('destroy-role', args=[role.id]))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.client.logout()

    def test_list_roles(self):
        self.client.force_authenticate(self.user)

        for i in range(3):
            self.create_role(self.user.active_company)

        response = self.client.get(reverse('list-roles'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), Role.objects.count())

        self.client.logout()

    def test_list_permissions(self):
        self.client.force_authenticate(self.user)

        response = self.client.get(reverse('list-permissions'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.logout()

    @staticmethod
    def create_role(company, name=None, permissions=None):
        if not name:
            name = "{} - {}".format(MTestCase.faker.name(), random.random())
        if not permissions:
            permissions = Permission.objects.all()[0:3]

        role = Role.objects.create(
            company=company,
            name=name,
        )
        role.permissions.set(permissions)
        role.save()
        return role
