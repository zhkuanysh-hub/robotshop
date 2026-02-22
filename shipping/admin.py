from django.contrib import admin

from .models import Shipment


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order",
        "carrier",
        "tracking_number",
        "status",
        "shipped_at",
        "delivered_at",
        "created_at",
    )
    search_fields = ("order__id", "carrier", "tracking_number")
    list_filter = ("status", "carrier", "created_at")
