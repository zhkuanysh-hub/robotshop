from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order",
        "amount",
        "provider",
        "transaction_id",
        "status",
        "paid_at",
        "created_at",
    )
    search_fields = ("order__id", "transaction_id", "provider")
    list_filter = ("status", "provider", "created_at")
