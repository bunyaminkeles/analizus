from django import forms
from .models import University


class OAIPMHKeywordForm(forms.Form):
    keyword = forms.CharField(
        max_length=300,
        label="Anahtar Kelime",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Başlık veya özette aranacak kelime...',
        })
    )
    year_from = forms.IntegerField(
        required=False,
        label="Başlangıç Yılı",
        min_value=1950,
        max_value=2026,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '2010'}),
    )
    year_to = forms.IntegerField(
        required=False,
        label="Bitiş Yılı",
        min_value=1950,
        max_value=2026,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '2024'}),
    )

    def clean(self):
        cleaned = super().clean()
        yf = cleaned.get('year_from')
        yt = cleaned.get('year_to')
        if yf and yt and yf > yt:
            raise forms.ValidationError("Başlangıç yılı bitiş yılından büyük olamaz.")
        return cleaned


class OAIPMHBrowseForm(forms.Form):
    university = forms.ModelChoiceField(
        queryset=University.objects.filter(is_active=True).order_by('name'),
        label="Üniversite",
        empty_label="-- Üniversite seçin --",
        widget=forms.Select(attrs={'class': 'form-select'}),
    )


class OAIPMHOrderForm(forms.Form):
    abstract_count = forms.IntegerField(
        label="İstenen Kayıt Sayısı",
        min_value=1,
        max_value=5000,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
    )
    payment_note = forms.CharField(
        label="Ödeme Notu (opsiyonel)",
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3,
                                     'placeholder': 'Havale açıklaması, banka dekontu bilgisi vb.'}),
    )
