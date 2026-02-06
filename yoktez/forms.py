from django import forms

KONU_CHOICES = [
    ('', '-- Bilim Alanı Seçin --'),
    ('Halk Sağlığı', 'Halk Sağlığı'),
    ('Sağlık Yönetimi', 'Sağlık Yönetimi'),
    ('Sağlık Kurumları Yönetimi', 'Sağlık Kurumları Yönetimi'),
    ('Hemşirelik', 'Hemşirelik'),
    ('Eğitim ve Öğretim', 'Eğitim ve Öğretim'),
    ('Psikoloji', 'Psikoloji'),
    ('İşletme', 'İşletme'),
    ('İktisat', 'İktisat'),
    ('Maliye', 'Maliye'),
    ('Biyoloji', 'Biyoloji'),
    ('Biyokimya', 'Biyokimya'),
    ('İstatistik', 'İstatistik'),
    ('Matematik', 'Matematik'),
    ('Fizik', 'Fizik'),
    ('Kimya', 'Kimya'),
    ('Bilgisayar Mühendisliği Bilimleri-Bilgisayar ve Kontrol', 'Bilgisayar Mühendisliği'),
    ('Makine Mühendisliği', 'Makine Mühendisliği'),
    ('Elektrik ve Elektronik Mühendisliği', 'Elektrik ve Elektronik Müh.'),
    ('İnşaat Mühendisliği', 'İnşaat Mühendisliği'),
    ('Gıda Mühendisliği', 'Gıda Mühendisliği'),
    ('Çevre Mühendisliği', 'Çevre Mühendisliği'),
    ('Hukuk', 'Hukuk'),
    ('Tarih', 'Tarih'),
    ('Sosyoloji', 'Sosyoloji'),
    ('Türk Dili ve Edebiyatı', 'Türk Dili ve Edebiyatı'),
    ('Dilbilim', 'Dilbilim'),
    ('Eczacılık ve Farmakoloji', 'Eczacılık ve Farmakoloji'),
    ('Geriatri', 'Geriatri'),
    ('Spor', 'Spor'),
]

INPUT_CSS = 'form-control bg-dark text-white border-secondary'
SELECT_CSS = 'form-select bg-dark text-white border-secondary'


class TezSearchForm(forms.Form):
    konu = forms.ChoiceField(
        choices=KONU_CHOICES,
        label="Bilim Alanı (Konu)",
        widget=forms.Select(attrs={'class': SELECT_CSS})
    )
    keyword1 = forms.CharField(
        max_length=100,
        label="Anahtar Kelime 1",
        widget=forms.TextInput(attrs={'class': INPUT_CSS, 'placeholder': 'Örneğin: obezite'})
    )
    keyword2 = forms.CharField(
        max_length=100, required=False,
        label="Anahtar Kelime 2 (Opsiyonel)",
        widget=forms.TextInput(attrs={'class': INPUT_CSS, 'placeholder': 'Opsiyonel'})
    )
    keyword3 = forms.CharField(
        max_length=100, required=False,
        label="Anahtar Kelime 3 (Opsiyonel)",
        widget=forms.TextInput(attrs={'class': INPUT_CSS, 'placeholder': 'Opsiyonel'})
    )


class TezOrderForm(forms.Form):
    abstract_count = forms.IntegerField(
        min_value=1, max_value=2000,
        label="İstenen Abstract Sayısı",
        widget=forms.NumberInput(attrs={'class': INPUT_CSS, 'value': 100})
    )
    payment_note = forms.CharField(
        required=False,
        label="Ödeme Açıklaması (havale açıklaması, tarih vb.)",
        widget=forms.Textarea(attrs={'class': INPUT_CSS, 'rows': 2, 'placeholder': 'Havale açıklamanızı yazın...'})
    )
