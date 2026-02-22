from django.contrib import admin

from .models import Order, OrderItem, OrderStatusHistory


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "total_amount", "created_at")
    search_fields = ("id", "user__username", "user__email", "address__city")
    list_filter = ("status", "created_at", "updated_at")


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "robot", "quantity", "unit_price", "created_at")
    search_fields = ("order__id", "robot__name")
    list_filter = ("created_at",)


@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "status", "comment", "created_at")
    search_fields = ("order__id", "comment")
    list_filter = ("status", "created_at")
