from django import forms
from django.db.models import Case, When, IntegerField
from .models import University

# Türkçe karakterleri ASCII eşdeğeriyle eşleştirerek sıralama anahtarı üretir
_TR_MAP = str.maketrans('ÇçĞğİıÖöŞşÜü', 'CcGgIiOoSsUu')


def _tr_sorted_universities():
    """Türkçe alfabetik sıraya göre sıralanmış aktif üniversite queryset'i döndürür."""
    # Veritabanı sorgusunu `__init__` içinde yapmak yerine, burada sadece sıralama mantığını
    # ve temel filtrelemeyi hazırlayabiliriz. Ancak mevcut yapı, `collectstatic` gibi
    # veritabanı hazır olmadan çalışabilen komutlarda sorun yaratıyor.
    # Bu nedenle, bu fonksiyonun çağrıldığı yerlerde (`__init__`) veritabanı sorgusu
    # yapılması daha güvenlidir.
    try:
        unis = list(University.objects.filter(is_active=True))
        unis.sort(key=lambda u: u.name.translate(_TR_MAP).lower())
        preserved = Case(
            *[When(pk=u.pk, then=i) for i, u in enumerate(unis)],
            output_field=IntegerField(),
        )
        return University.objects.filter(is_active=True).annotate(_order=preserved).order_by('_order')
    except Exception:
        # Eğer veritabanı hazır değilse (örn. migrations öncesi), boş queryset döndür
        return University.objects.none()

class OAIPMHKeywordForm(forms.Form):
    keyword = forms.CharField(
        required=False,
        max_length=300,
        label="Başlık",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Başlıkta aranacak kelime...',
        })
    )
    abstract_query = forms.CharField(
        required=False,
        max_length=300,
        label="Özet",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Özette aranacak kelime...',
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
    universities = forms.ModelMultipleChoiceField(
        queryset=University.objects.none(),  # Başlangıçta boş queryset
        required=False,
        label="Üniversiteler",
        help_text="Seçim yapılmazsa tüm üniversitelerde aranır.",
        widget=forms.CheckboxSelectMultiple(),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Queryset'i form instance'ı oluşturulurken ata
        self.fields['universities'].queryset = _tr_sorted_universities()

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get('keyword') and not cleaned.get('abstract_query'):
            raise forms.ValidationError("En az bir arama terimi girilmeli (başlık veya özet).")
        yf = cleaned.get('year_from')
        yt = cleaned.get('year_to')
        if yf and yt and yf > yt:
            raise forms.ValidationError("Başlangıç yılı bitiş yılından büyük olamaz.")
        return cleaned


class OAIPMHBrowseForm(forms.Form):
    university = forms.ModelChoiceField(
        queryset=University.objects.none(), # Başlangıçta boş queryset
        label="Üniversite",
        empty_label="-- Üniversite seçin --",
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Queryset'i form instance'ı oluşturulurken ata
        self.fields['university'].queryset = _tr_sorted_universities()


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