from django import forms
from .models import Booking


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['date_from', 'date_to', 'notes']
        labels = {
            'date_from': 'من تاريخ',
            'date_to': 'إلى تاريخ',
            'notes': 'ملاحظات (اختياري)',
        }
        widgets = {
            'date_from': forms.DateInput(attrs={'type': 'date'}),
            'date_to': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def clean(self):
        cleaned = super().clean()
        date_from = cleaned.get('date_from')
        date_to = cleaned.get('date_to')
        if date_from and date_to and date_to <= date_from:
            raise forms.ValidationError('تاريخ الانتهاء يجب أن يكون بعد تاريخ البداية.')
        return cleaned
