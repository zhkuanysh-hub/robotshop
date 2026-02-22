from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class WishlistItem(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wishlist_items",
    )
    robot = models.ForeignKey(
        "catalog.Robot",
        on_delete=models.CASCADE,
        related_name="wishlist_items",
    )

    class Meta:
        unique_together = ("user", "robot")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} -> {self.robot}"
