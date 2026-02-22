from django.contrib import admin

from .models import Address, Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "phone", "birth_date", "created_at")
    search_fields = ("user__username", "user__email", "phone")
    list_filter = ("created_at",)


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "label",
        "full_name",
        "city",
        "country",
        "is_default",
        "created_at",
    )
    search_fields = ("user__username", "full_name", "city", "country", "postal_code")
    list_filter = ("country", "city", "is_default", "created_at")
