from django import forms


TUR_CHOICES = [
    ('0', 'Hepsi'),
    ('1', 'Yüksek Lisans'),
    ('2', 'Doktora'),
    ('3', 'Tıpta Uzmanlık'),
    ('4', 'Sanatta Yeterlik'),
]


class YokTezSearchForm(forms.Form):
    tez_ad = forms.CharField(
        required=False,
        label='Tez Adı / Anahtar Kelime',
        widget=forms.TextInput(attrs={
            'class': 'form-control bg-dark text-white border-secondary',
            'placeholder': 'Tez başlığında ara...',
        }),
    )
    metin = forms.CharField(
        required=False,
        label='Özet / Metin',
        widget=forms.TextInput(attrs={
            'class': 'form-control bg-dark text-white border-secondary',
            'placeholder': 'Özet içinde ara...',
        }),
    )
    tur = forms.ChoiceField(
        required=False,
        label='Tez Türü',
        choices=TUR_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select bg-dark text-white border-secondary'}),
    )
    yil_baslangic = forms.IntegerField(
        required=False,
        label='Başlangıç Yılı',
        widget=forms.NumberInput(attrs={
            'class': 'form-control bg-dark text-white border-secondary',
            'placeholder': '2000',
            'min': '1950',
            'max': '2030',
        }),
    )
    yil_bitis = forms.IntegerField(
        required=False,
        label='Bitiş Yılı',
        widget=forms.NumberInput(attrs={
            'class': 'form-control bg-dark text-white border-secondary',
            'placeholder': '2024',
            'min': '1950',
            'max': '2030',
        }),
    )

    def clean(self):
        cleaned = super().clean()
        # En az bir alan dolu olmalı
        fields = ['tez_ad', 'metin']
        if not any(cleaned.get(f) for f in fields):
            raise forms.ValidationError('En az bir arama kriteri girmelisiniz.')
        return cleaned
