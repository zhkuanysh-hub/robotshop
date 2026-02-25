from django.contrib import admin

from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("user", "robot", "rating", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("user__username", "robot__name")
    readonly_fields = ("created_at", "updated_at")
    list_select_related = ("user", "robot")
