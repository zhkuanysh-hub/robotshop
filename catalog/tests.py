from django.test import TestCase
from django.urls import reverse

from .models import Brand, Category, Robot


class CatalogViewsTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Home Robots", slug="home-robots")
        self.brand = Brand.objects.create(name="Auronix")
        self.robot = Robot.objects.create(
            name="Helper One",
            slug="helper-one",
            category=self.category,
            brand=self.brand,
            price="1000.00",
            stock=5,
            is_active=True,
        )

    def test_catalog_list_page_200(self):
        response = self.client.get(reverse("catalog:list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "catalog/robot_list.html")

    def test_robot_detail_page_200(self):
        response = self.client.get(reverse("catalog:detail", kwargs={"slug": self.robot.slug}))
        self.assertEqual(response.status_code, 200)
