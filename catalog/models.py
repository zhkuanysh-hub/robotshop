from django.core.validators import MinValueValidator
from django.db import models

from apps.core.models import TimeStampedModel


class Category(TimeStampedModel):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Brand(TimeStampedModel):
    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Tag(TimeStampedModel):
    name = models.CharField(max_length=80, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Robot(TimeStampedModel):
    name = models.CharField(max_length=180)
    slug = models.SlugField(max_length=200, unique=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="robots",
    )
    brand = models.ForeignKey(
        Brand,
        on_delete=models.PROTECT,
        related_name="robots",
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name="robots")
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class RobotImage(TimeStampedModel):
    robot = models.ForeignKey(
        Robot,
        on_delete=models.CASCADE,
        related_name="images",
    )
    image_url = models.URLField(max_length=500)
    alt_text = models.CharField(max_length=255, blank=True)
    is_main = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self):
        return f"{self.robot.name} image #{self.id}"


class Specification(TimeStampedModel):
    name = models.CharField(max_length=120)
    unit = models.CharField(max_length=40, blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="specifications",
    )

    class Meta:
        unique_together = ("name", "category")
        ordering = ["name"]

    def __str__(self):
        return f"{self.category.name}: {self.name}"


class RobotSpecValue(TimeStampedModel):
    robot = models.ForeignKey(
        Robot,
        on_delete=models.CASCADE,
        related_name="spec_values",
    )
    specification = models.ForeignKey(
        Specification,
        on_delete=models.CASCADE,
        related_name="values",
    )
    value = models.CharField(max_length=255)

    class Meta:
        unique_together = ("robot", "specification")
        ordering = ["specification__name"]

    def __str__(self):
        return f"{self.robot.name} - {self.specification.name}: {self.value}"
