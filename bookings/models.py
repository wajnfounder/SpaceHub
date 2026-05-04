from django.db import models
from django.contrib.auth.models import User
from spaces.models import Space
from django.db.models import F


class BookingStatus(models.TextChoices):
    PENDING = 'pending', 'قيد الانتظار'
    CONFIRMED = 'confirmed', 'مؤكد'
    CANCELLED = 'cancelled', 'ملغي'
    COMPLETED = 'completed', 'مكتمل'


class Booking(models.Model):
    """نموذج الحجز — ForeignKey مع Space و User"""

    space = models.ForeignKey(
        Space,
        on_delete=models.CASCADE,
        related_name='bookings',
        verbose_name='المساحة'
    )
    tenant = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='bookings',
        verbose_name='المستأجر'
    )
    date_from = models.DateField(verbose_name='من تاريخ')
    date_to = models.DateField(verbose_name='إلى تاريخ')
    status = models.CharField(
        max_length=20,
        choices=BookingStatus.choices,
        default=BookingStatus.PENDING,
        verbose_name='الحالة'
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='السعر الإجمالي'
    )
    notes = models.TextField(blank=True, verbose_name='ملاحظات')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'حجز'
        verbose_name_plural = 'الحجوزات'

    def __str__(self):
        return f"حجز {self.space.title} بواسطة {self.tenant.username}"

    def duration_days(self):
        return (self.date_to - self.date_from).days or 1
