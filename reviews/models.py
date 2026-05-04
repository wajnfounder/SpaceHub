from django.db import models
from django.contrib.auth.models import User
from spaces.models import Space
from django.core.validators import MinValueValidator, MaxValueValidator


class Review(models.Model):
    space   = models.ForeignKey(Space, on_delete=models.CASCADE,
                                related_name='reviews', verbose_name='المساحة')
    user    = models.ForeignKey(User,  on_delete=models.CASCADE,
                                related_name='reviews', verbose_name='المستخدم')

    # Overall rating
    rating  = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='التقييم العام (1-5)'
    )
    comment = models.TextField(verbose_name='التعليق')

    # Multi-criteria ratings (each optional 1-5)
    cleanliness   = models.IntegerField(null=True, blank=True,
                                        validators=[MinValueValidator(1), MaxValueValidator(5)],
                                        verbose_name='النظافة')
    internet      = models.IntegerField(null=True, blank=True,
                                        validators=[MinValueValidator(1), MaxValueValidator(5)],
                                        verbose_name='الإنترنت')
    parking_rate  = models.IntegerField(null=True, blank=True,
                                        validators=[MinValueValidator(1), MaxValueValidator(5)],
                                        verbose_name='مواقف السيارات')
    quietness     = models.IntegerField(null=True, blank=True,
                                        validators=[MinValueValidator(1), MaxValueValidator(5)],
                                        verbose_name='الهدوء')
    host_service  = models.IntegerField(null=True, blank=True,
                                        validators=[MinValueValidator(1), MaxValueValidator(5)],
                                        verbose_name='خدمة المالك')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['space', 'user']
        verbose_name = 'تقييم'
        verbose_name_plural = 'التقييمات'

    def __str__(self):
        return f"{self.user.username} — {self.space.title} ({self.rating}/5)"

    def criteria_avg(self):
        vals = [v for v in [self.cleanliness, self.internet,
                             self.parking_rate, self.quietness, self.host_service]
                if v is not None]
        return round(sum(vals) / len(vals), 1) if vals else None
