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
    
    # Checkbox (HTML'de manuel olsa da burada tanımlı olması veri doğrulaması için iyidir)
    terms_confirmed = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label="Kullanım Şartları",
        error_messages={'required': 'Kayıt olmak için şartları kabul etmelisiniz.'}
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email") # Şifre alanları (password1/2) otomatiktir.

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
        fields = ['title', 'description', 'budget_min', 'budget_max', 'category']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control bg-dark text-light border-secondary', 'placeholder': 'Örn: SPSS Veri Analizi'}),
            'description': forms.Textarea(attrs={'class': 'form-control bg-dark text-light border-secondary', 'rows': 5, 'placeholder': 'İşin detaylarını açıklayın...'}),
            'budget_min': forms.NumberInput(attrs={'class': 'form-control bg-dark text-light border-secondary', 'placeholder': 'Min'}),
            'budget_max': forms.NumberInput(attrs={'class': 'form-control bg-dark text-light border-secondary', 'placeholder': 'Max'}),
            'category': forms.Select(attrs={'class': 'form-select bg-dark text-light border-secondary'}),
        }
        labels = {
            'title': 'İlan Başlığı',
            'description': 'İş Tanımı',
            'budget_min': 'Minimum Bütçe (TL)',
            'budget_max': 'Maksimum Bütçe (TL)',
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