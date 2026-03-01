from django import forms

INPUT_CSS = 'form-control bg-dark text-white border-secondary'
LABEL_CSS = 'form-label text-light fw-semibold'

ALLOWED_EXTENSIONS = {'.bib', '.txt', '.csv', '.tsv'}
MAX_FILE_SIZE_MB = 10


class BibliometricUploadForm(forms.Form):
    file = forms.FileField(
        label='Veri Dosyası',
        help_text='BibTeX (.bib), Web of Science veya Scopus CSV/TSV (.csv, .txt) formatları desteklenir. Maks 10 MB.',
        widget=forms.FileInput(attrs={
            'class': INPUT_CSS,
            'accept': '.bib,.csv,.tsv,.txt',
        }),
    )

    def clean_file(self):
        f = self.cleaned_data['file']
        name = f.name.lower()
        ext = '.' + name.rsplit('.', 1)[-1] if '.' in name else ''

        if ext not in ALLOWED_EXTENSIONS:
            raise forms.ValidationError(
                f'Desteklenmeyen dosya formatı: {ext}. '
                f'Lütfen .bib, .csv, .tsv veya .txt yükleyin.'
            )

        size_mb = f.size / (1024 * 1024)
        if size_mb > MAX_FILE_SIZE_MB:
            raise forms.ValidationError(
                f'Dosya boyutu çok büyük ({size_mb:.1f} MB). '
                f'Maksimum {MAX_FILE_SIZE_MB} MB yükleyebilirsiniz.'
            )
        return f


class BibliometricOrderForm(forms.Form):
    payment_note = forms.CharField(
        required=False,
        label='Ödeme Açıklaması',
        help_text='EFT/Havale açıklaması, tarih vb.',
        widget=forms.Textarea(attrs={
            'class': INPUT_CSS,
            'rows': 3,
            'placeholder': 'Havale/EFT yaptığınıza dair kısa açıklama...',
        }),
    )
