from django.contrib import admin

from .models import OTPRecord


@admin.register(OTPRecord)
class OTPRecordAdmin(admin.ModelAdmin):
    list_display = ("id", "phone_number", "otp", "created_at")
    list_filter = ("created_at",)
    search_fields = ("phone_number", "otp")
    readonly_fields = ("created_at",)
