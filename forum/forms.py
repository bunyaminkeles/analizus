from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Topic, Post, FreelanceJob, JobProposal, TopicTag
from django.utils.safestring import mark_safe

# --- 1. KAYIT FORMU ---
class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label="E-Posta Adresi",
        help_text="Geçerli bir e-posta adresi giriniz."
    )

    # Checkbox
    terms_confirmed = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label="Kullanım Şartları",
        error_messages={'required': 'Kayıt olmak için şartları kabul etmelisiniz.'}
    )

    # Honeypot — botlar doldurur, insanlar görmez
    website = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'style': 'position:absolute;left:-9999px;top:-9999px;',
            'tabindex': '-1',
            'autocomplete': 'off',
        })
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")

    def clean_website(self):
        # Bot honeypot'u doldurdu
        if self.cleaned_data.get('website'):
            raise forms.ValidationError("Geçersiz kayıt.")
        return ''

    def clean_username(self):
        import re
        username = self.cleaned_data.get('username', '')
        username_lower = username.lower()

        # Kural 1: 2+ adet q/w/x → kesinlikle bot
        if sum(1 for c in username_lower if c in 'qwx') >= 2:
            raise forms.ValidationError("Geçerli bir kullanıcı adı seçin.")

        # Kural 2: 4+ ardışık ünsüz → bot imzası
        if re.search(r'[bcçdfgğhjklmnpqrsştvwxyz]{4,}', username_lower):
            raise forms.ValidationError("Geçerli bir kullanıcı adı seçin (örn: ahmet42, bilge_ar).")

        # Kural 3: Aynı karakter 3+ kez art arda (yikeeofuuu → uuu)
        if re.search(r'(.)\1\1', username_lower):
            raise forms.ValidationError("Geçerli bir kullanıcı adı seçin.")

        # Kural 4: Skor tabanlı rastgele isim tespiti
        # Yalnızca 8–12 karakter, tamamı küçük harf ve sadece harf olan kullanıcı adlarına uygulanır
        if re.match(r'^[a-z]{8,12}$', username_lower):
            vowels = set('aeıioöuü')  # y dahil değil → daha sıkı
            vowel_count = sum(1 for c in username_lower if c in vowels)
            vowel_ratio = vowel_count / len(username_lower)

            # Max ardışık ünsüz (y ünsüz sayılır burada)
            consonant_groups = re.findall(r'[bcçdfgğhjklmnpqrsştvwxyz]+', username_lower)
            max_cons = max((len(g) for g in consonant_groups), default=0)

            score = 0
            if max_cons >= 3:       score += 2
            if vowel_ratio < 0.30:  score += 2
            if vowel_ratio < 0.25:  score += 1   # ekstra ceza
            if len(username_lower) in (9, 10, 11): score += 1  # bot uzunluk kalıbı

            # Yüksek ünlü oranı gerçek isim işareti → puanı düşür
            if vowel_ratio >= 0.40:
                score = max(0, score - 2)

            if score >= 3:
                raise forms.ValidationError(
                    "Geçerli bir kullanıcı adı seçin (örn: ahmet42, bilge_ar)."
                )

        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Bu e-posta adresi sistemde zaten kayıtlı.")
        return email

# --- 2. YENİ KONU FORMU ---
class NewTopicForm(forms.ModelForm):
    message = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 10, 'placeholder': 'İçeriği buraya yazın...'}),
        label="Mesaj",
        max_length=4000
    )
    tags = forms.ModelMultipleChoiceField(
        queryset=TopicTag.objects.none(),  # import-sırasında DB sorgusu çalışmasın
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'tag-checkbox-list'}),
        required=False,
        label="Etiketler"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Form örneği oluşturulurken gerçek queryset'i ata (DB erişimi burada güvenlidir)
        self.fields['tags'].queryset = TopicTag.objects.filter(is_active=True)

    class Meta:
        model = Topic
        fields = ['subject', 'tags']
        widgets = {
            'subject': forms.TextInput(attrs={'placeholder': 'Konu Başlığı'}),
        }

# --- 3. CEVAP FORMU ---
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Cevabınızı yazın...'}),
        }

# --- 4. İŞ İLANI FORMU ---
class JobPostForm(forms.ModelForm):
    class Meta:
        model = FreelanceJob
        fields = ['title', 'description', 'budget_max', 'category']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control bg-dark text-light border-secondary', 'placeholder': 'Örn: SPSS Veri Analizi'}),
            'description': forms.Textarea(attrs={'class': 'form-control bg-dark text-light border-secondary', 'rows': 5, 'placeholder': 'İşin detaylarını açıklayın...'}),
            'budget_max': forms.NumberInput(attrs={'class': 'form-control bg-dark text-light border-secondary', 'placeholder': 'Örn: 3 gün'}),
            'category': forms.Select(attrs={'class': 'form-select bg-dark text-light border-secondary'}),
        }
        labels = {
            'title': 'İlan Başlığı',
            'description': 'İş Tanımı',
            'budget_max': 'Bütçe (TL)',
            'category': 'Kategori',
        }

class ProposalForm(forms.ModelForm):
    class Meta:
        model = JobProposal
        fields = ['price', 'duration', 'message']
        widgets = {
            'price': forms.NumberInput(attrs={'class': 'form-control bg-dark text-light border-secondary', 'placeholder': 'Teklifiniz (TL)'}),
            'duration': forms.TextInput(attrs={'class': 'form-control bg-dark text-light border-secondary', 'placeholder': 'Örn: 3 gün'}),
            'message': forms.Textarea(attrs={'class': 'form-control bg-dark text-light border-secondary', 'rows': 3, 'placeholder': 'Neden sizi seçmeliyim?'}),
        }
        labels = {
            'price': 'Teklif Tutarı (TL)',
            'duration': 'Tahmini Süre',
            'message': 'Ön Yazı',
        }