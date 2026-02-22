from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.core.models import TimeStampedModel


class Review(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    robot = models.ForeignKey(
        "catalog.Robot",
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    title = models.CharField(max_length=120, blank=True)
    comment = models.TextField(blank=True)
    is_published = models.BooleanField(default=True)

    class Meta:
        unique_together = ("user", "robot")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.robot} ({self.rating}/5)"
