from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class StatsAccessTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(username="user", password="pass12345")
        self.staff = user_model.objects.create_user(
            username="staff",
            password="pass12345",
            is_staff=True,
        )

    def test_stats_requires_staff(self):
        self.client.force_login(self.user)
        response_user = self.client.get(reverse("core:stats"))
        self.assertIn(response_user.status_code, (302, 403))

        self.client.force_login(self.staff)
        response_staff = self.client.get(reverse("core:stats"))
        self.assertEqual(response_staff.status_code, 200)
