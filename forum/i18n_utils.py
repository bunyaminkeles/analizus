"""E-posta ve bildirimlerde alıcının dilini kullanma yardımcıları.

E-postanın dili, isteği yapanın değil ALICININ diliyle belirlenir
(Profile.preferred_language). Admin'e giden bildirimler her zaman Türkçe.
"""
from django.conf import settings
from django.utils import translation

SUPPORTED = {code for code, _ in settings.LANGUAGES}


def user_language(user):
    """Kullanıcının kayıtlı dil tercihi; bilinmiyorsa varsayılan dil (tr)."""
    lang = getattr(getattr(user, 'profile', None), 'preferred_language', None)
    return lang if lang in SUPPORTED else settings.LANGUAGE_CODE


def recipient_language(user):
    """`with recipient_language(user):` — bloktaki gettext/render_to_string/reverse
    alıcının dilinde çalışır."""
    return translation.override(user_language(user))


def admin_language():
    """Admin/ekip bildirimleri her zaman Türkçe."""
    return translation.override(settings.LANGUAGE_CODE)
