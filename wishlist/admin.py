from django.contrib import admin

from .models import WishlistItem


@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "robot", "created_at")
    search_fields = ("user__username", "user__email", "robot__name")
    list_filter = ("created_at",)
