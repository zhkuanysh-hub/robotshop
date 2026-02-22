from django.contrib import admin

from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "robot", "user", "rating", "is_published", "created_at")
    search_fields = ("robot__name", "user__username", "title", "comment")
    list_filter = ("rating", "is_published", "created_at")
