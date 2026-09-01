from django.contrib import admin

from .models import OTPRecord


@admin.register(OTPRecord)
class OTPRecordAdmin(admin.ModelAdmin):
    list_display = ("id", "phone_number", "sender", "otp", "created_at")
    list_filter = ("sender", "created_at")
    search_fields = ("phone_number", "sender", "otp")
    readonly_fields = ("created_at",)
