from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from accounts.models import Address
from .models import Order


class OrderAccessTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user1 = user_model.objects.create_user(username="user1", password="pass12345")
        self.user2 = user_model.objects.create_user(username="user2", password="pass12345")

        self.address1 = Address.objects.create(
            user=self.user1,
            full_name="User One",
            phone="+77000000001",
            country="KZ",
            city="Almaty",
            line1="Street 1",
            postal_code="050000",
        )
        self.order = Order.objects.create(
            user=self.user1,
            address=self.address1,
            total_amount="1000.00",
        )

    def test_orders_list_requires_login(self):
        response = self.client.get(reverse("orders:list"))
        self.assertEqual(response.status_code, 302)

    def test_orders_detail_requires_owner_or_staff(self):
        self.client.force_login(self.user2)
        response_other_user = self.client.get(reverse("orders:detail", kwargs={"pk": self.order.pk}))
        self.assertIn(response_other_user.status_code, (302, 403, 404))

        self.client.force_login(self.user1)
        response_owner = self.client.get(reverse("orders:detail", kwargs={"pk": self.order.pk}))
        self.assertEqual(response_owner.status_code, 200)
