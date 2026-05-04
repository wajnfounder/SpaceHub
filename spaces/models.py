from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg


class SpaceType(models.TextChoices):
    OFFICE        = 'office',        'مكتب'
    HALL          = 'hall',          'قاعة'
    STUDIO        = 'studio',        'استوديو'
    WAREHOUSE     = 'warehouse',     'مستودع'
    EVENT         = 'event',         'مساحة فعاليات'
    MEETING       = 'meeting',       'قاعة اجتماعات'
    COWORKING     = 'coworking',     'مساحة عمل مشتركة'
    TRAINING      = 'training',      'غرفة تدريب'


class SpaceStatus(models.TextChoices):
    AVAILABLE   = 'available',   'متاح'
    UNAVAILABLE = 'unavailable', 'غير متاح'


class City(models.TextChoices):
    RIYADH  = 'riyadh',  'الرياض'
    JEDDAH  = 'jeddah',  'جدة'
    MAKKAH  = 'makkah',  'مكة المكرمة'
    DAMMAM  = 'dammam',  'الدمام'
    MADINAH = 'madinah', 'المدينة المنورة'


class RentalType(models.TextChoices):
    DAILY   = 'daily',   'يومي'
    MONTHLY = 'monthly', 'شهري'
    YEARLY  = 'yearly',  'سنوي'


class AmenityIcon(models.TextChoices):
    SCREEN      = 'screen',      'شاشة عرض'
    COFFEE      = 'coffee',      'كورنر قهوة'
    PARKING     = 'parking',     'مواقف سيارات'
    WIFI        = 'wifi',        'إنترنت عالي السرعة'
    AC          = 'ac',          'تكييف مركزي'
    WHITEBOARD  = 'whiteboard',  'لوح أبيض'
    PROJECTOR   = 'projector',   'بروجكتر'
    KITCHEN     = 'kitchen',     'مطبخ صغير'
    PRINTER     = 'printer',     'طابعة'
    RECEPTION   = 'reception',   'استقبال'
    SECURITY    = 'security',    'حراسة أمنية'
    ELEVATOR    = 'elevator',    'مصعد'


AMENITY_FA = {
    'screen':     'fas fa-tv',
    'coffee':     'fas fa-coffee',
    'parking':    'fas fa-parking',
    'wifi':       'fas fa-wifi',
    'ac':         'fas fa-snowflake',
    'whiteboard': 'fas fa-chalkboard',
    'projector':  'fas fa-film',
    'kitchen':    'fas fa-utensils',
    'printer':    'fas fa-print',
    'reception':  'fas fa-concierge-bell',
    'security':   'fas fa-shield-alt',
    'elevator':   'fas fa-arrow-up',
}


class Space(models.Model):
    owner       = models.ForeignKey(User, on_delete=models.CASCADE,
                                    related_name='spaces', verbose_name='المالك')
    title       = models.CharField(max_length=200, verbose_name='اسم المساحة')
    description = models.TextField(verbose_name='الوصف')
    space_type  = models.CharField(max_length=20, choices=SpaceType.choices,
                                   default=SpaceType.OFFICE, verbose_name='نوع المساحة')
    status      = models.CharField(max_length=20, choices=SpaceStatus.choices,
                                   default=SpaceStatus.AVAILABLE, verbose_name='الحالة')
    city        = models.CharField(max_length=20, choices=City.choices,
                                   default=City.RIYADH, verbose_name='المدينة')
    address     = models.CharField(max_length=300, verbose_name='العنوان')

    # Pricing
    price_per_day   = models.DecimalField(max_digits=10, decimal_places=2,
                                          verbose_name='السعر / يوم (ريال)')
    price_monthly   = models.DecimalField(max_digits=10, decimal_places=2,
                                          null=True, blank=True, verbose_name='السعر / شهر (ريال)')
    price_yearly    = models.DecimalField(max_digits=10, decimal_places=2,
                                          null=True, blank=True, verbose_name='السعر / سنة (ريال)')
    rental_type     = models.CharField(max_length=10, choices=RentalType.choices,
                                       default=RentalType.DAILY, verbose_name='نوع الإيجار')

    capacity   = models.IntegerField(default=1, verbose_name='السعة (أشخاص)')
    area_sqm   = models.FloatField(default=0,   verbose_name='المساحة (م²)')

    # Media & Location
    maps_embed_url = models.URLField(blank=True, verbose_name='رابط تضمين خرائط Google')

    # Dynamic pricing flag
    allow_dynamic_pricing = models.BooleanField(default=False)
    discount_pct          = models.PositiveSmallIntegerField(default=0,
                                                              null=True, blank=True,
                                                             verbose_name='نسبة الخصم %')

    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'مساحة'
        verbose_name_plural = 'المساحات'

    def __str__(self):
        return f"{self.title} — {self.get_city_display()}"

    def average_rating(self):
     try:
        result = self.reviews.aggregate(avg=Avg('rating'))
        return result['avg'] or 0
     except:
        return 0

    def main_image(self):
        img = self.images.first()
        return img.image if img else None

    def effective_price(self):
        """Price after dynamic discount."""
        p = self.price_per_day
        if self.allow_dynamic_pricing and self.discount_pct:
            p = p * (100 - self.discount_pct) / 100
        return p

    def is_large_venue(self):
        """Determines if the space should show additional services."""
        return self.space_type in (SpaceType.HALL, SpaceType.EVENT,
                                   SpaceType.TRAINING, SpaceType.COWORKING)


class SpaceImage(models.Model):
    space   = models.ForeignKey(Space, on_delete=models.CASCADE, related_name='images')
    image   = models.ImageField(upload_to='spaces/', verbose_name='صورة')
    is_main = models.BooleanField(default=False, verbose_name='صورة رئيسية')

    def __str__(self):
        return f"صورة لـ {self.space.title}"


class SpaceAmenity(models.Model):
    """Features / amenities a space provides."""
    space = models.ForeignKey(Space, on_delete=models.CASCADE, related_name='amenities')
    name  = models.CharField(max_length=30, choices=AmenityIcon.choices,
                             verbose_name='الميزة')

    class Meta:
        unique_together = ['space', 'name']
        verbose_name = 'ميزة'
        verbose_name_plural = 'المميزات'

    def __str__(self):
        return f"{self.space.title} — {self.get_name_display()}"

    @property
    def icon(self):
        return AMENITY_FA.get(self.name, 'fas fa-check')


class AdditionalService(models.Model):
    """Optional add-on services (for large venues only)."""

    class ServiceType(models.TextChoices):
        CATERING      = 'catering',      'ضيافة وتقديم طعام'
        PHOTOGRAPHY   = 'photography',   'تصوير فوتوغرافي'
        DECORATION    = 'decoration',    'ديكور وتنسيق'
        ORGANIZERS    = 'organizers',    'منظمو فعاليات'
        SOUND         = 'sound',         'نظام صوت'
        CHAIRS        = 'chairs',        'كراسي وطاولات إضافية'
        SECURITY_SVC  = 'security_svc',  'خدمة أمن'
        CLEANING      = 'cleaning',      'تنظيف ما بعد الفعالية'

    space        = models.ForeignKey(Space, on_delete=models.CASCADE,
                                     related_name='additional_services')
    service_type = models.CharField(max_length=20, choices=ServiceType.choices)
    price        = models.DecimalField(max_digits=8, decimal_places=2,
                                       verbose_name='السعر (ريال)')
    description  = models.CharField(max_length=200, blank=True, verbose_name='وصف مختصر')

    class Meta:
        unique_together = ['space', 'service_type']
        verbose_name = 'خدمة إضافية'
        verbose_name_plural = 'الخدمات الإضافية'

    def __str__(self):
        return f"{self.space.title} — {self.get_service_type_display()}"
