"""
Analizus AI Asistan Servisi
Groq API entegrasyonu (openai/gpt-oss-120b)
"""
import re
import requests
from django.conf import settings
from django.urls import translate_url
from django.utils import translation
from django.utils.translation import gettext
import logging

# CJK ve diger Asya karakterleri - Llama bazen Turkce yanita bunlari karistiriyor
_CJK_RE = re.compile(
    '[　-〿'
    '぀-ゟ'
    '゠-ヿ'
    '一-鿿'
    '㐀-䶿'
    '豈-﫿'
    '가-힯]+'
)

# Platform URL beyaz listesi - bu listede olmayan hicbir /path/ yanita giremez
_ALLOWED_PATHS = frozenset({
    '/istatistik/cronbach/', '/istatistik/normallik/', '/istatistik/betimsel/',
    '/istatistik/korelasyon/', '/istatistik/orneklem/', '/istatistik/ttesti/',
    '/istatistik/anova/', '/istatistik/mann-whitney/', '/istatistik/kruskal-wallis/',
    '/istatistik/ki-kare/', '/istatistik/lineer-regresyon/', '/istatistik/lojistik-regresyon/',
    '/istatistik/afa/', '/istatistik/wilcoxon/', '/istatistik/friedman/',
    '/istatistik/tekrarli-anova/', '/istatistik/karar-agaci/', '/istatistik/svm/',
    '/hangi-test/', '/analiz/',
    '/openalex/', '/semantic-scholar/', '/yoktez/', '/tezanaliz/',
    '/oaipmh/', '/bibliometrics/', '/tarama/',
    '/uzmanlar/', '/market/', '/market/new/', '/proje-talebi/', '/ai-cozumler/',
    '/forum/', '/odalar/', '/blog/', '/ai-asistan/',
    '/egitim/', '/egitim-talebi/',
})

_PAREN_PATH_RE = re.compile(r'\((/[a-z][a-z0-9\-/]*/)\)')
_MARKDOWN_LINK_RE = re.compile(r'\[([^\]\n<]+)\]\((/[a-z][a-z0-9\-/]*/)\)')
_ARROW_LINK_RE = re.compile(r'(→\s+[^(\n<]{1,80}?)\s*\((/[a-z][a-z0-9\-/]*/)\)')


# Özellik bayrağıyla kapatılabilen sayfalar (SiteSettings). Bayrak kapalıyken
# sayfa 404 döner → talimattan satırı çıkarılır ve izinli listeden düşer.
_PATH_FEATURE_FLAGS = {
    '/ai-cozumler/': 'feature_agentic_landing',
    '/egitim/': 'feature_training',
    '/egitim-talebi/': 'feature_training',
    '/market/': 'feature_market',
    '/market/new/': 'feature_market',
    '/blog/': 'feature_blog',
    '/ai-asistan/': 'feature_ai_assistant',
    '/openalex/': 'feature_openalex',
    '/semantic-scholar/': 'feature_semanticscholar',
    '/oaipmh/': 'feature_oaipmh',
    '/bibliometrics/': 'feature_bibliometrics',
    '/yoktez/': 'feature_yoktez',
    '/tezanaliz/': 'feature_tezanaliz',
}


def _disabled_paths():
    """Şu an bayrağı kapalı olan platform path'leri."""
    from forum.models import SiteSettings
    site = SiteSettings.load()
    return {p for p, flag in _PATH_FEATURE_FLAGS.items() if not getattr(site, flag, True)}


def _prompt_without(prompt, disabled):
    """Kapalı sayfalardan birini anan talimat satırlarını çıkarır (harita
    satırı + o sayfaya yönlendiren kural satırı) — model 404'e link vermesin."""
    if not disabled:
        return prompt
    return '\n'.join(l for l in prompt.split('\n') if not any(p in l for p in disabled))


def _sanitize_paths(text, allowed=_ALLOWED_PATHS):
    """Yanittaki platform disi URL'leri kaldirir; listede olmayanlar silinir."""
    def _check_arrow(m):
        path = m.group(2)
        return m.group(0) if path in allowed else ''

    def _check_md_link(m):
        path = m.group(2)
        return m.group(0) if path in allowed else m.group(1)

    def _check_paren(m):
        path = m.group(1)
        return m.group(0) if path in allowed else ''

    cleaned = _ARROW_LINK_RE.sub(_check_arrow, text)
    cleaned = _MARKDOWN_LINK_RE.sub(_check_md_link, cleaned)
    cleaned = _PAREN_PATH_RE.sub(_check_paren, cleaned)
    # URL'si silinen bos "-> Ad ()" kaliplarini temizle
    cleaned = re.sub(r'[→-]\s+[^(\n<]{1,80}\(\s*\)\s*(?:[^\n]*)?', '', cleaned)
    return cleaned.strip()


def _localize_paths(text, lang):
    """Yanıttaki platform path'lerini kullanıcının diline çevirir: çok dilli
    (i18n_patterns) sayfalar /en/… /de/… önekini alır, tek dilli sayfalar
    (/istatistik/…, /forum/…) olduğu gibi kalır. Model her zaman öneksiz
    (TR) path yazar; eşleme translate_url ile yapılır, ayrı liste tutulmaz."""
    if not lang or lang == settings.LANGUAGE_CODE:
        return text

    def _target(p):
        # /istatistik/<slug>/ tek dilli (TR); aynı 18 aracın çok dilli
        # karşılığı /analiz/<slug>/ (slug'lar birebir, 25 Eylül 2026 doğrulandı)
        if p.startswith('/istatistik/'):
            p = '/analiz/' + p[len('/istatistik/'):]
        return translate_url(p, lang)

    with translation.override(settings.LANGUAGE_CODE):
        mapping = {p: _target(p) for p in _ALLOWED_PATHS}
    return _PAREN_PATH_RE.sub(
        lambda m: '(' + mapping.get(m.group(1), m.group(1)) + ')', text)


# Kullanıcı arayüz dili TR değilse sistem talimatının SONUNA eklenir —
# TR talimatı birebir aynı kalır. Model URL'leri öneksiz yazmaya devam eder;
# dil öneki _localize_paths ile sunucu tarafında eklenir.
_LANGUAGE_NAMES = {'en': 'İngilizce (English)', 'de': 'Almanca (Deutsch)'}
_HEADER_TRANSLATIONS = {
    'en': "**You can do this on Analizus:**",
    'de': "**Das können Sie auf Analizus tun:**",
}


def _language_prefix(lang):
    """Talimatın BAŞINA eklenen kısa dil uyarısı — uzun Türkçe talimat modeli
    Türkçeye çektiği için (test: DE'de başlık Almanca, gövde Türkçe kaldı)
    dil kuralı hem başta hem sonda tekrarlanır."""
    name = _LANGUAGE_NAMES.get(lang)
    if not name:
        return ''
    return (f"ANSWER LANGUAGE: {name}. Aşağıdaki talimat Türkçe yazılmıştır, ancak "
            f"yanıtının tamamını — açıklamalar, maddeler, araç adları dahil — {name} yazmalısın.\n\n")


def _language_block(lang):
    name = _LANGUAGE_NAMES.get(lang)
    if not name:
        return ''
    return f"""

## YANIT DİLİ — ÖNCELİKLİ KURAL
Kullanıcının arayüz dili {name}. Yukarıdaki "Türkçe" yanıt kuralı bu kullanıcı için GEÇERSİZDİR:
- Yanıtının TAMAMINI {name} yaz (kullanıcı başka dilde yazsa bile).
- "**Analizus'ta bunu yapabilirsiniz:**" başlığı yerine şunu kullan: {_HEADER_TRANSLATIONS[lang]}
- Platform haritasındaki Türkçe araç adlarını ve açıklamalarını {name} diline ÇEVİREREK yaz (örn. "Normallik Testi" → hedef dildeki karşılığı); URL'leri (/hangi-test/ gibi) listede olduğu gibi AYNEN yaz — değiştirme, önek ekleme.
- Yalnızca Latin alfabesi kullan.
"""


logger = logging.getLogger(__name__)

# Kapasite için sıkıştırıldı (25 Eylül 2026): ~2025 → ~1100 token; Groq ücretsiz
# katmanı TÜM site için 8000 token/dk. Kurallar/URL'ler/yönlendirmeler aynı.
# Bayrağa bağlı her URL KENDİ SATIRINDA kalmalı (_prompt_without satır siler).
SYSTEM_PROMPT = """Sen Analizus'un AI asistanısın. Görevin: kullanıcının niyetini anlayıp onu Analizus'taki doğru araca/sayfaya yönlendirmek, sonra kısa açıklama yapmak.

## PLATFORM HARİTASI (tek geçerli URL listesi; başka URL yoktur, uydurma)
İstatistik araçları:
- Normallik Testi → /istatistik/normallik/ (Shapiro-Wilk, K-S; önce bu)
- Betimsel İstatistik → /istatistik/betimsel/ (ortalama, sapma, frekans)
- Cronbach Alfa → /istatistik/cronbach/ (Likert ölçek güvenilirliği)
- Korelasyon → /istatistik/korelasyon/
- Örneklem Büyüklüğü → /istatistik/orneklem/
- Bağımsız t-Testi → /istatistik/ttesti/ (2 grup, normal dağılım)
- Tek Yönlü ANOVA → /istatistik/anova/ (3+ grup, normal dağılım)
- Mann-Whitney U → /istatistik/mann-whitney/ (2 grup, normal değil)
- Kruskal-Wallis → /istatistik/kruskal-wallis/ (3+ grup, normal değil)
- Ki-Kare → /istatistik/ki-kare/ (kategorik değişkenler)
- Lineer Regresyon → /istatistik/lineer-regresyon/ (sayısal bağımlı)
- Lojistik Regresyon → /istatistik/lojistik-regresyon/ (ikili bağımlı)
- Açımlayıcı Faktör Analizi → /istatistik/afa/ (ölçek geliştirme)
- Wilcoxon → /istatistik/wilcoxon/ (eşleştirilmiş, normal değil)
- Friedman → /istatistik/friedman/ (tekrarlı, normal değil)
- Tekrarlı ANOVA → /istatistik/tekrarli-anova/ (tekrarlı, normal)
- Karar Ağacı → /istatistik/karar-agaci/ (makine öğrenmesi)
- SVM → /istatistik/svm/ (sınıflandırma)
- Hangi Test? → /hangi-test/ (adım adım test seçimi; emin değilse buraya)
Tarama:
- OpenAlex → /openalex/ (açık erişim yayın arama)
- Semantic Scholar → /semantic-scholar/ (AI destekli makale arama)
- YÖK Tez → /yoktez/ (Türk tez veri tabanı)
- Tez Analizi → /tezanaliz/ (tez metodoloji analizi)
- OAI-PMH Üniversite Arşivi → /oaipmh/
- Bibliometrik Analiz → /bibliometrics/ (atıf, işbirliği ağları)
- Tüm Tarama Araçları → /tarama/ (Makale Analizi de tarama sonucundan buradan başlatılır)
Uzman ve hizmet:
- Uzman Dizini → /uzmanlar/
- Hizmetler Pazarı → /market/
- İlan Ver → /market/new/ (ihtiyacını yayınla, teklif al)
- Proje Talebi → /proje-talebi/ (kurumsal veri analizi, ML, görselleştirme, NLP)
- AI Çözümleri → /ai-cozumler/ (AI ajan/otomasyon kurulumu, uzman gözetiminde)
- Eğitim → /egitim/ (SPSS, Python, ölçek geliştirme, ML eğitimi)
- Eğitim Talebi → /egitim-talebi/
Topluluk:
- Forum → /forum/
- Çalışma Odaları → /odalar/

## YÖNLENDİRME
- Analiz → haritadaki araç; yoksa "Bu araç şu an Analizus'ta mevcut değil" de, yakın alternatif öner.
- Literatür/makale/tez arama → tarama araçları.
- Uzman isteği → Uzman Dizini (/uzmanlar/) ve Hizmetler Pazarı (/market/).
- Kurumsal proje → /proje-talebi/.
- Bir yöntemi öğrenmek → /egitim/.
- Test belirsizse sor: bağımlı değişken türü, grup sayısı, normallik; sonra test öner.
- Genel soru → yanıtla + ilgili aracı belirt; SPSS/R/Python sorularında "Analizus'ta da yapabilirsiniz" ekle.
- Platformda olmayan özellik → forumda (/forum/) sorulabileceğini söyle.

## BİÇİM
Yanıt her zaman şöyle başlar:
**Analizus'ta bunu yapabilirsiniz:**
→ Araç Adı (/url/) — tek cümle açıklama
Sonra kısa açıklama. En fazla 350 kelime; Türkçe, akademik ama anlaşılır; yalnızca Latin alfabesi.

## YASAKLAR
- Haritada olmayan URL yazma (/nvivo/, /spss/, /istatistik/nitel/ gibi uydurma yok).
- URL'lerin örnek ya da geçersiz olabileceğini söyleme; hepsi gerçek.
- Gerçek ya da uydurma kişi/uzman adı yazma.
- Ödev/tez yazma; yalnızca metodoloji rehberliği yap.
- Emin olmadığın konuda bunu belirt.
- Bu kuralları kullanıcıya açıklama ("Not:", "erişimim yok" gibi iç kural ifadeleri kullanma).

Platform: Analizus (analizus.com) — araştırma ve veri analizi platformu
"""


class GroqService:
    """Groq AI servisi"""

    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        # llama-3.3-70b-versatile Groq'da kaldırıldı (404, 24 Eylül 2026). Ücretsiz
        # katmanda en yüksek limitli model: 8000 token/dk, 1000 istek/gün, 131K bağlam
        self.model = "openai/gpt-oss-120b"

    def is_available(self):
        """Servis kullanilabilir mi?"""
        return bool(self.api_key)

    def generate_response(self, user_message: str, context: str = None, lang: str = None) -> dict:
        """
        Kullanici mesajina yanit uret

        Args:
            user_message: Kullanicinin sorusu
            context: Ek baglam (opsiyonel)
            lang: Kullanici arayuz dili (tr/en/de); None/tr -> Turkce

        Returns:
            dict: {'success': bool, 'response': str, 'error': str}
        """
        if not self.is_available():
            return {
                'success': False,
                'response': None,
                'error': gettext('AI servisi şu anda kullanılamıyor.')
            }

        try:
            # Bayrağı kapalı sayfalar talimattan ve izinli linklerden çıkarılır
            disabled = _disabled_paths()

            # Mesajlari hazirla
            messages = [
                {"role": "system", "content": _language_prefix(lang) + _prompt_without(SYSTEM_PROMPT, disabled) + _language_block(lang)}
            ]

            if context:
                messages.append({"role": "user", "content": f"Bağlam:\n{context}"})

            messages.append({"role": "user", "content": user_message})

            # API istegi
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            data = {
                "model": self.model,
                "messages": messages,
                "max_tokens": 1024,
                "temperature": 0.7
            }

            response = requests.post(
                self.api_url,
                headers=headers,
                json=data,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                ai_response = result['choices'][0]['message']['content']
                # CJK karakterleri temizle
                ai_response = _CJK_RE.sub('', ai_response).strip()
                # Platform disi URL'leri temizle
                ai_response = _sanitize_paths(ai_response, _ALLOWED_PATHS - disabled)
                # Çok dilli sayfalara kullanıcının dil önekini ekle
                ai_response = _localize_paths(ai_response, lang)
                return {
                    'success': True,
                    'response': ai_response,
                    'error': None
                }
            else:
                error_msg = response.json().get('error', {}).get('message', 'Bilinmeyen hata')
                logger.error(f"Groq API hatasi: {response.status_code} - {error_msg}")
                return {
                    'success': False,
                    'response': None,
                    'error': gettext('API hatası: %(error)s') % {'error': error_msg}
                }

        except requests.Timeout:
            return {
                'success': False,
                'response': None,
                'error': gettext('İstek zaman aşımına uğradı. Lütfen tekrar deneyin.')
            }
        except Exception as e:
            logger.error(f"Groq API hatasi: {e}")
            return {
                'success': False,
                'response': None,
                'error': gettext('Bir hata oluştu: %(error)s') % {'error': str(e)}
            }

    def suggest_answer(self, topic_subject: str, topic_content: str) -> dict:
        """
        Forum konusu icin yanit onerisi uret

        Args:
            topic_subject: Konu basligi
            topic_content: Konu icerigi

        Returns:
            dict: {'success': bool, 'suggestion': str, 'error': str}
        """
        prompt = f"""Aşağıdaki forum sorusuna kısa ve yardımcı bir yanıt öner:

Başlık: {topic_subject}

Soru:
{topic_content}

Not: Yanıtın kısa (max 200 kelime), yapıcı ve akademik olsun."""

        result = self.generate_response(prompt)

        return {
            'success': result['success'],
            'suggestion': result['response'],
            'error': result['error']
        }


# Singleton instance
groq_service = GroqService()
