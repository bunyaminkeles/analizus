"""
Güvenlik middleware'leri: Honeypot + E-posta doğrulama + Son görülme + NoIndex
"""
from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from django.utils import timezone
from django.utils.translation import gettext

_HONEYPOT_FIELD = 'website'
_GUARDED_PATHS = {'/login/', '/register/'}

# last_seen en fazla bu sıklıkta yazılır (saniye) — gereksiz DB yazımını önler
_LAST_SEEN_INTERVAL = 60


class NoIndexMiddleware:
    """Production dışı ortamlarda (dev/staging) tüm yanıtlara noindex header'ı ekler.
    Production davranışı (settings.IS_PRODUCTION) değişmez."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if not settings.IS_PRODUCTION:
            response['X-Robots-Tag'] = 'noindex, nofollow'
        return response


class ForceDefaultLanguageMiddleware:
    """Tarayıcının Accept-Language header'ına göre otomatik dil algılamayı
    kapatır. Kullanıcı navbar'daki dil seçiciden açıkça seçim yapmadıkça
    (django_language çerezi set edilmeden) site her zaman varsayılan dille
    (LANGUAGE_CODE = 'tr') açılır — /en/ veya /de/ URL prefix'i her zaman
    çalışmaya devam eder, bu yalnızca prefix'siz (varsayılan) istekleri
    etkiler. LocaleMiddleware'den ÖNCE çalışmalı (bkz. settings.MIDDLEWARE)."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if settings.LANGUAGE_COOKIE_NAME not in request.COOKIES:
            request.META['HTTP_ACCEPT_LANGUAGE'] = ''
        return self.get_response(request)


class MultilingualFeatureMiddleware:
    """`feature_multilingual` flag'i kapalıyken /en/, /de/ gibi varsayılan
    olmayan dil prefix'li URL'leri 404 ile keser. i18n_patterns URLconf'ta
    her zaman statik olarak kayıtlı (request-time'da DB'ye göre değiştirilemez)
    — bu middleware, flag'i dinamik olarak uygulamanın tek yolu.
    LocaleMiddleware'den ÖNCE çalışabilir, sadece ham path string'ine bakar."""

    def __init__(self, get_response):
        self.get_response = get_response
        self._non_default_prefixes = tuple(
            f'/{code}/' for code, _ in settings.LANGUAGES if code != settings.LANGUAGE_CODE
        )

    def __call__(self, request):
        if request.path_info.startswith(self._non_default_prefixes):
            from forum.models import SiteSettings
            if not SiteSettings.load().feature_multilingual:
                from django.http import Http404
                raise Http404("Çok dilli yayın şu an kapalı.")
        return self.get_response(request)


class VisitorCounterMiddleware:
    """Her sayfa isteğinde (bot dahil) ziyaretçi sayacını artırır."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if (
            not request.path.startswith(('/static/', '/media/', '/admin/', '/api/'))
            and request.method == 'GET'
        ):
            try:
                from forum.models import SiteVisit
                SiteVisit.increment()
            except Exception:
                pass
        return self.get_response(request)


class LastSeenMiddleware:
    """Giriş yapmış kullanıcının last_seen alanını dakikada bir günceller."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if (
            request.user.is_authenticated
            and hasattr(request.user, 'profile')
            and not request.path.startswith('/static/')
            and not request.path.startswith('/media/')
        ):
            profile = request.user.profile
            now = timezone.now()
            if (
                profile.last_seen is None
                or (now - profile.last_seen).total_seconds() > _LAST_SEEN_INTERVAL
            ):
                profile.last_seen = now
                profile.save(update_fields=['last_seen'])
        return self.get_response(request)


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
        'new_topic',
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
        messages.warning(request, gettext('Bu özelliği kullanmak için e-posta adresinizi doğrulamanız gerekiyor.'))
        return redirect('verification_pending')


class PreferredLanguageMiddleware:
    """Giriş yapmış kullanıcının dil tercihini (Profile.preferred_language)
    e-postalar için günceller. LocaleMiddleware'den SONRA çalışmalı.

    - /en/ /de/ önekli bir sayfa ziyaret edilirse o dil kaydedilir.
    - Dil seçici (i18n/setlang/ POST) ile seçilen dil (tr dahil) kaydedilir.
    - Öneksiz sayfalar (forum, blog…) tercihi tr'ye ÇEVİRMEZ — bu sayfalar
      tek dilli olduğundan kullanıcının seçimini yansıtmaz.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, 'user', None)
        if user is not None and user.is_authenticated:
            lang = None
            if request.method == 'POST' and request.path_info.rstrip('/').endswith('/i18n/setlang'):
                lang = request.POST.get('language')
            else:
                from django.utils.translation import get_language_from_path
                lang = get_language_from_path(request.path_info)
            if lang and lang in {code for code, _ in settings.LANGUAGES}:
                profile = getattr(user, 'profile', None)
                if profile is not None and profile.preferred_language != lang:
                    type(profile).objects.filter(pk=profile.pk).update(preferred_language=lang)
                    profile.preferred_language = lang
        return self.get_response(request)
