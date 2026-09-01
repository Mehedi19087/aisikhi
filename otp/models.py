from django.db import models


class OTPRecord(models.Model):
    phone_number = models.CharField(max_length=32, db_index=True)
    sender = models.CharField(max_length=64, blank=True, default="", db_index=True)
    otp = models.CharField(max_length=16, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "OTP Record"
        verbose_name_plural = "OTP Records"

    def __str__(self):
        if self.sender:
            return f"{self.phone_number} ({self.sender}) - {self.otp}"
        return f"{self.phone_number} - {self.otp}"
