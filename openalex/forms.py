import json
from django import forms

FIELD_CHOICES = [
    ('title', 'Başlık'),
    ('abstract', 'Özet'),
    ('author', 'Yazar'),
    ('keyword', 'Anahtar Kelime'),
    ('year', 'Yıl Aralığı'),
]

# Kazımada hâlâ kullanılabilen ama form UI'ında gösterilmeyen alanlar
_SCRAPER_ONLY_FIELDS = ['journal', 'institution', 'doi', 'type']
VALID_FIELDS = [c[0] for c in FIELD_CHOICES] + _SCRAPER_ONLY_FIELDS

INPUT_CSS = 'form-control bg-dark text-white border-secondary'


class AlexSearchForm(forms.Form):
    """OpenAlex gelişmiş arama formu. Sorgu parçaları JSON olarak gönderilir."""
    query_parts_json = forms.CharField(
        widget=forms.HiddenInput(),
        required=True,
    )

    def clean_query_parts_json(self):
        raw = self.cleaned_data['query_parts_json']
        try:
            parts = json.loads(raw)
        except json.JSONDecodeError:
            raise forms.ValidationError('Geçersiz sorgu formatı.')

        if not isinstance(parts, list) or len(parts) == 0:
            raise forms.ValidationError('En az bir arama kriteri gereklidir.')

        if len(parts) > 10:
            raise forms.ValidationError('En fazla 10 arama kriteri eklenebilir.')

        for part in parts:
            if not isinstance(part, dict):
                raise forms.ValidationError('Geçersiz sorgu parçası.')
            if part.get('field') not in VALID_FIELDS:
                raise forms.ValidationError(f"Geçersiz alan: {part.get('field')}")
            if not part.get('value', '').strip():
                raise forms.ValidationError('Boş değer girilemez.')
            if part.get('operator') not in ('AND', 'OR', None, ''):
                raise forms.ValidationError('Geçersiz operatör.')

        return parts


class AlexOrderForm(forms.Form):
    abstract_count = forms.IntegerField(
        min_value=1, max_value=5000,
        label="İstenen Yayın Sayısı",
        widget=forms.NumberInput(attrs={'class': INPUT_CSS, 'value': 100})
    )
    payment_note = forms.CharField(
        required=False,
        label="Ödeme Açıklaması (havale açıklaması, tarih vb.)",
        widget=forms.Textarea(attrs={'class': INPUT_CSS, 'rows': 2, 'placeholder': 'Havale açıklamanızı yazın...'})
    )
