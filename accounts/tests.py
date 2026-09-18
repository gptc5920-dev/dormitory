from rest_framework.test import APITestCase

from .models import User


class AuthenticationTests(APITestCase):
    def test_manager_can_login(self):
        User.objects.create_user(username="manager", password="StrongPass123!", role=User.Role.MANAGER)
        response = self.client.post("/api/auth/login/", {"username": "manager", "password": "StrongPass123!"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.data)
