import json
from django import forms
from django.utils.translation import gettext, gettext_lazy

# Arama sayfasında seçilebilen alanlar (sıra = açılır listedeki sıra)
FIELD_CHOICES = [
    ('title', gettext_lazy('Başlık')),
    ('tiab', gettext_lazy('Başlık/Özet')),
    ('author', gettext_lazy('Yazar')),
    ('keyword', gettext_lazy('Anahtar Kelime')),
    ('mesh', gettext_lazy('MeSH Terimi')),
    ('journal', gettext_lazy('Dergi/Kaynak')),
    ('affiliation', gettext_lazy('Kurum')),
    ('year', gettext_lazy('Yıl Aralığı')),
]
VALID_FIELDS = [c[0] for c in FIELD_CHOICES] + ['doi', 'type']


class PubMedSearchForm(forms.Form):
    """PubMed gelişmiş arama formu. Sorgu parçaları JSON olarak gönderilir; parçalar AND ile birleşir."""
    query_parts_json = forms.CharField(widget=forms.HiddenInput(), required=True)

    def clean_query_parts_json(self):
        raw = self.cleaned_data['query_parts_json']
        try:
            parts = json.loads(raw)
        except json.JSONDecodeError:
            raise forms.ValidationError(gettext('Geçersiz sorgu formatı.'))

        if not isinstance(parts, list) or len(parts) == 0:
            raise forms.ValidationError(gettext('En az bir arama kriteri gereklidir.'))
        if len(parts) > 10:
            raise forms.ValidationError(gettext('En fazla 10 arama kriteri eklenebilir.'))

        cleaned = []
        for part in parts:
            if not isinstance(part, dict):
                raise forms.ValidationError(gettext('Geçersiz sorgu parçası.'))
            if part.get('field') not in VALID_FIELDS:
                raise forms.ValidationError(gettext("Geçersiz alan: {field}").format(field=part.get('field')))
            value = str(part.get('value', '')).strip()
            if not value:
                raise forms.ValidationError(gettext('Boş değer girilemez.'))
            cleaned.append({'field': part['field'], 'value': value[:300], 'operator': 'AND'})
        return cleaned
