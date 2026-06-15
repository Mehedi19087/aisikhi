from django.contrib import admin

from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "order_type",
        "ai_subscription_plan",
        "amount",
        "status",
        "payment_method",
        "created_at",
    )
    list_filter = ("order_type", "status", "payment_method", "created_at")
    search_fields = ("user__email", "transaction_id", "activation_gmail")
    readonly_fields = ("created_at", "updated_at")
