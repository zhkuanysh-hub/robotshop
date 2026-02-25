from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from catalog.models import Brand, Category, Robot
from reviews.models import Review


class ReviewRatingValidationTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username="reviewer",
            password="secret123",
        )
        self.category = Category.objects.create(name="Home", slug="home")
        self.brand = Brand.objects.create(name="Auronix")
        self.robot = Robot.objects.create(
            name="Helper Bot",
            slug="helper-bot",
            category=self.category,
            brand=self.brand,
            price="1000.00",
            stock=5,
        )

    def test_rating_zero_raises_validation_error(self):
        review = Review(user=self.user, robot=self.robot, rating=0)
        with self.assertRaises(ValidationError):
            review.full_clean()

    def test_rating_six_raises_validation_error(self):
        review = Review(user=self.user, robot=self.robot, rating=6)
        with self.assertRaises(ValidationError):
            review.full_clean()

    def test_rating_within_range_is_valid(self):
        review = Review(user=self.user, robot=self.robot, rating=4)
        review.full_clean()
        review.save()
        self.assertEqual(review.rating, 4)
