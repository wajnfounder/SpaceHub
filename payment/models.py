from django.db import models
from django.contrib.auth.models import User
from bookings.models import Booking


class PaymentMethod(models.TextChoices):
    MADA       = 'mada',      'مدى'
    APPLE_PAY  = 'apple_pay', 'Apple Pay'
    CREDIT     = 'credit',    'بطاقة ائتمان'
    CASH       = 'cash',      'نقداً'


class PaymentStatus(models.TextChoices):
    PENDING   = 'pending',   'قيد الانتظار'
    COMPLETED = 'completed', 'مكتمل'
    FAILED    = 'failed',    'فشل'
    REFUNDED  = 'refunded',  'مُسترجع'


class Payment(models.Model):
    booking    = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment')
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    method     = models.CharField(max_length=20, choices=PaymentMethod.choices, default=PaymentMethod.MADA)
    status     = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    amount     = models.DecimalField(max_digits=10, decimal_places=2)
    reference  = models.CharField(max_length=64, blank=True)   # mock transaction ID
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'دفعة'
        verbose_name_plural = 'المدفوعات'

    def __str__(self):
        return f"Payment #{self.pk} — {self.booking} ({self.status})"
