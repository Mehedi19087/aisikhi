from django.contrib import admin

from .models import UserAISubscription


@admin.register(UserAISubscription)
class UserAISubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "plan",
        "order",
        "status",
        "delivery_status",
        "starts_at",
        "ends_at",
    )
    list_filter = ("status", "delivery_status", "created_at")
    search_fields = ("user__email", "activation_gmail", "plan__title")
    readonly_fields = ("created_at", "updated_at")
