from django.contrib import admin

from .models import (
    Brand,
    Category,
    Robot,
    RobotImage,
    RobotSpecValue,
    Specification,
    Tag,
)


class RobotImageInline(admin.TabularInline):
    model = RobotImage
    extra = 1
    fields = ("image_url", "alt_text", "is_main", "sort_order")


@admin.action(description="Mark selected robots as available")
def make_available(modeladmin, request, queryset):
    updated = queryset.update(is_active=True)
    modeladmin.message_user(request, f"{updated} robot(s) marked as available.")


@admin.action(description="Mark selected robots as unavailable")
def make_unavailable(modeladmin, request, queryset):
    updated = queryset.update(is_active=False)
    modeladmin.message_user(request, f"{updated} robot(s) marked as unavailable.")


@admin.register(Robot)
class RobotAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "slug",
        "category",
        "brand",
        "price",
        "stock",
        "is_active",
        "created_at",
    )
    search_fields = ("name", "slug", "description", "brand__name", "category__name")
    list_filter = ("is_active", "category", "brand", "created_at")
    prepopulated_fields = {"slug": ("name",)}
    filter_horizontal = ("tags",)
    inlines = (RobotImageInline,)
    actions = (make_available, make_unavailable)
    readonly_fields = ("created_at", "updated_at")
    list_select_related = ("category", "brand")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug", "is_active", "created_at")
    search_fields = ("name", "slug", "description")
    list_filter = ("is_active", "created_at")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at", "updated_at")


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "is_active", "created_at")
    search_fields = ("name", "description")
    list_filter = ("is_active", "created_at")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_at")
    search_fields = ("name",)
    list_filter = ("created_at",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(Specification)
class SpecificationAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "category", "unit", "created_at")
    search_fields = ("name", "category__name", "unit")
    list_filter = ("category", "created_at")
    readonly_fields = ("created_at", "updated_at")
    list_select_related = ("category",)


@admin.register(RobotImage)
class RobotImageAdmin(admin.ModelAdmin):
    list_display = ("id", "robot", "is_main", "sort_order", "created_at")
    search_fields = ("robot__name", "alt_text", "image_url")
    list_filter = ("is_main", "created_at")
    readonly_fields = ("created_at", "updated_at")
    list_select_related = ("robot",)


@admin.register(RobotSpecValue)
class RobotSpecValueAdmin(admin.ModelAdmin):
    list_display = ("id", "robot", "specification", "value", "created_at")
    search_fields = ("robot__name", "specification__name", "value")
    list_filter = ("specification", "created_at")
    readonly_fields = ("created_at", "updated_at")
    list_select_related = ("robot", "specification")
