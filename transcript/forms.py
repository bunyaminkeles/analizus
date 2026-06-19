from django import forms


COMMON_LANGUAGES = [
    ("", "Otomatik (tr → de → en)"),
    ("tr", "Türkçe"),
    ("de", "Almanca"),
    ("en", "İngilizce"),
    ("fr", "Fransızca"),
    ("es", "İspanyolca"),
    ("ar", "Arapça"),
    ("ru", "Rusça"),
    ("zh", "Çince"),
    ("ja", "Japonca"),
    ("pt", "Portekizce"),
    ("it", "İtalyanca"),
    ("ko", "Korece"),
]

DELIVERY_CHOICES = [
    ("download", "İndir (TXT)"),
    ("email", "E-posta ile gönder"),
]


class TranscriptRequestForm(forms.Form):
    video_url = forms.URLField(
        label="YouTube Video Linki",
        widget=forms.URLInput(attrs={
            "placeholder": "https://www.youtube.com/watch?v=...",
            "class": "ax-form-control",
            "autocomplete": "off",
        }),
    )
    language = forms.ChoiceField(
        label="Dil",
        choices=COMMON_LANGUAGES,
        required=False,
        widget=forms.Select(attrs={"class": "ax-form-select"}),
    )
    delivery = forms.ChoiceField(
        label="Teslimat",
        choices=DELIVERY_CHOICES,
        widget=forms.RadioSelect(attrs={"class": "ax-radio"}),
        initial="download",
    )
    email = forms.EmailField(
        label="E-posta adresi",
        required=False,
        widget=forms.EmailInput(attrs={
            "placeholder": "ornek@email.com",
            "class": "ax-form-control",
        }),
        help_text="Teslimat 'e-posta' seçildiğinde zorunludur.",
    )

    def clean(self):
        cleaned = super().clean()
        delivery = cleaned.get("delivery")
        email = cleaned.get("email")
        if delivery == "email" and not email:
            self.add_error("email", "E-posta ile gönderim için e-posta adresi zorunludur.")
        return cleaned
