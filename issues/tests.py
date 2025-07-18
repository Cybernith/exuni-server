from rest_framework.test import APITestCase
from django.urls import reverse
from users.models import User


class IssueCreateTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user('u', 'u@u.com', 'pass')
        self.client.force_authenticate(self.user)
        self.url = reverse('sendIssue')

    def test_create_bug(self):
        data = {
            "title": "Test Bug",
            "description": "Details",
            "issue_type": "bug",
            "severity": 2
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['issue_type'], 'bug')
