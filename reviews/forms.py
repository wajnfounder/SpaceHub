from django import forms
from .models import Review

STAR_CHOICES = [(i, str(i)) for i in range(1, 6)]
OPT_CHOICES  = [('', ' — ')] + STAR_CHOICES


class ReviewForm(forms.ModelForm):
    rating       = forms.ChoiceField(choices=STAR_CHOICES, widget=forms.RadioSelect,
                                     label='التقييم العام')
    cleanliness  = forms.ChoiceField(choices=OPT_CHOICES, required=False, label='النظافة')
    internet     = forms.ChoiceField(choices=OPT_CHOICES, required=False, label='الإنترنت')
    parking_rate = forms.ChoiceField(choices=OPT_CHOICES, required=False, label='المواقف')
    quietness    = forms.ChoiceField(choices=OPT_CHOICES, required=False, label='الهدوء')
    host_service = forms.ChoiceField(choices=OPT_CHOICES, required=False, label='خدمة المالك')

    class Meta:
        model  = Review
        fields = ['rating', 'comment',
                  'cleanliness', 'internet', 'parking_rate', 'quietness', 'host_service']
        labels  = {'comment': 'تعليقك'}
        widgets = {'comment': forms.Textarea(attrs={'rows': 3})}

    def _to_int(self, key):
        v = self.cleaned_data.get(key)
        return int(v) if v else None

    def clean_rating(self):       return int(self.cleaned_data['rating'])
    def clean_cleanliness(self):  return self._to_int('cleanliness')
    def clean_internet(self):     return self._to_int('internet')
    def clean_parking_rate(self): return self._to_int('parking_rate')
    def clean_quietness(self):    return self._to_int('quietness')
    def clean_host_service(self): return self._to_int('host_service')
