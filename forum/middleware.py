"""
Güvenlik middleware'leri: Honeypot + E-posta doğrulama
"""
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages

_HONEYPOT_FIELD = 'website'
_GUARDED_PATHS = {'/login/', '/register/'}


class HoneypotMiddleware:
    """POST'ta gizli 'website' alanı dolu gelirse botu sessizce reddeder."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if (
            request.method == 'POST'
            and request.path in _GUARDED_PATHS
            and request.POST.get(_HONEYPOT_FIELD)
        ):
            return HttpResponseRedirect(request.path)
        return self.get_response(request)


class EmailVerificationMiddleware:
    """
    Doğrulanmamış kullanıcıların belirli sayfalara erişimini kısıtlar
    """

    # Bu URL'lere doğrulanmamış kullanıcılar erişebilir
    ALLOWED_URLS = [
        'home',
        'login',
        'logout',
        'register',
        'verification_pending',
        'verify_email',
        'resend_verification',
        'about',
        'contact',
        'search',
        'category_topics',
        'topic_detail',
        'profile_detail',
        'section_detail',
        'health_check',
    ]

    # Bu URL prefix'leri her zaman izinli
    ALLOWED_PREFIXES = [
        '/admin/',
        '/static/',
        '/media/',
        '/api/',  # Tüm API endpoint'leri
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Giriş yapmamış kullanıcılar için kontrol yok
        if not request.user.is_authenticated:
            return self.get_response(request)

        # Admin kullanıcıları her zaman geçer
        if request.user.is_staff or request.user.is_superuser:
            return self.get_response(request)

        # Profil yoksa geç (yeni kayıt olmuş olabilir)
        if not hasattr(request.user, 'profile'):
            return self.get_response(request)

        # E-posta doğrulanmışsa geç
        if request.user.profile.email_verified:
            return self.get_response(request)

        # İzin verilen prefix'leri kontrol et
        for prefix in self.ALLOWED_PREFIXES:
            if request.path.startswith(prefix):
                return self.get_response(request)

        # URL adını kontrol et
        try:
            from django.urls import resolve
            url_name = resolve(request.path).url_name
            if url_name in self.ALLOWED_URLS:
                return self.get_response(request)
        except Exception:
            pass

        # Diğer tüm sayfalar için doğrulama gerekli
        messages.warning(request, 'Bu özelliği kullanmak için e-posta adresinizi doğrulamanız gerekiyor.')
        return redirect('verification_pending')
