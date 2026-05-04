from django import forms
from django.forms import inlineformset_factory
from .models import Space, SpaceImage, SpaceAmenity, AdditionalService


class SpaceForm(forms.ModelForm):
    class Meta:
        model  = Space
        fields = [
            'title', 'description', 'space_type', 'city', 'address',
            'price_per_day', 'price_monthly', 'price_yearly', 'rental_type',
            'capacity', 'area_sqm', 'status',
            'maps_embed_url', 'discount_pct',
        ]
        labels = {
            'title': 'اسم المساحة', 'description': 'الوصف',
            'space_type': 'نوع المساحة', 'city': 'المدينة', 'address': 'العنوان',
            'price_per_day': 'السعر / يوم (ريال)',
            'price_monthly': 'السعر / شهر (ريال)',
            'price_yearly':  'السعر / سنة (ريال)',
            'rental_type': 'نوع الإيجار',
            'capacity': 'السعة (أشخاص)', 'area_sqm': 'المساحة (م²)',
            'status': 'الحالة',
            'maps_embed_url': 'رابط تضمين خرائط Google',
            'discount_pct': 'نسبة الخصم %',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class SpaceImageForm(forms.ModelForm):
    class Meta:
        model  = SpaceImage
        fields = ['image', 'is_main']
        labels = {'image': 'الصورة', 'is_main': 'صورة رئيسية'}


# Inline formsets used in the owner management area
SpaceAmenityFormSet      = inlineformset_factory(Space, SpaceAmenity,
                                                  fields=['name'],
                                                  extra=4, can_delete=True)
AdditionalServiceFormSet = inlineformset_factory(Space, AdditionalService,
                                                  fields=['service_type', 'price', 'description'],
                                                  extra=3, can_delete=True)
