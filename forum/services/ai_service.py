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
    '/openalex/', '/semantic-scholar/', '/yoktez/', '/tezanaliz/', '/makaleanaliz/',
    '/oaipmh/', '/bibliometrics/', '/tarama/',
    '/uzmanlar/', '/market/', '/market/new/', '/proje-talebi/', '/ai-cozumler/',
    '/forum/', '/odalar/', '/blog/', '/ai-asistan/',
    '/egitim/', '/egitim-talebi/',
})

_PAREN_PATH_RE = re.compile(r'\((/[a-z][a-z0-9\-/]*/)\)')
_MARKDOWN_LINK_RE = re.compile(r'\[([^\]\n<]+)\]\((/[a-z][a-z0-9\-/]*/)\)')
_ARROW_LINK_RE = re.compile(r'(→\s+[^(\n<]{1,80}?)\s*\((/[a-z][a-z0-9\-/]*/)\)')


def _sanitize_paths(text):
    """Yanittaki platform disi URL'leri kaldirir; listede olmayanlar silinir."""
    def _check_arrow(m):
        path = m.group(2)
        return m.group(0) if path in _ALLOWED_PATHS else ''

    def _check_md_link(m):
        path = m.group(2)
        return m.group(0) if path in _ALLOWED_PATHS else m.group(1)

    def _check_paren(m):
        path = m.group(1)
        return m.group(0) if path in _ALLOWED_PATHS else ''

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
    with translation.override(settings.LANGUAGE_CODE):
        mapping = {p: translate_url(p, lang) for p in _ALLOWED_PATHS}
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
Kullanıcının arayüz dili {name}. Yukarıdaki "Türkçe yanıt ver" ve "yalnızca Türkçe" kuralları bu kullanıcı için GEÇERSİZDİR:
- Yanıtının TAMAMINI {name} yaz (kullanıcı başka dilde yazsa bile).
- "**Analizus'ta bunu yapabilirsiniz:**" başlığı yerine şunu kullan: {_HEADER_TRANSLATIONS[lang]}
- Platform haritasındaki Türkçe araç adlarını ve açıklamalarını {name} diline ÇEVİREREK yaz (örn. "Normallik Testi" → hedef dildeki karşılığı); URL'leri (/hangi-test/ gibi) listede olduğu gibi AYNEN yaz — değiştirme, önek ekleme.
- Yalnızca Latin alfabesi kullan.
"""


logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Sen Analizus platformunun özel AI asistanısın. Görevin yalnızca genel bilgi vermek değil — kullanıcının ne yapmak istediğini anlayıp onu Analizus platformundaki doğru araca, sayfaya veya hizmete yönlendirmektir.

## PLATFORM HARİTASI — GERÇEK VE AKTİF URL'LER

Aşağıdaki URL'ler analizus.com'da GERÇEKTEN MEVCUT ve aktif sayfalardır. Bu listede OLMAYAN hiçbir URL yoktur — uydurma.

### İstatistik Araçları
Kullanıcı analiz yapmak istediğinde doğru URL'yi ver:

- Normallik Testi → /istatistik/normallik/ (Shapiro-Wilk, Kolmogorov-Smirnov — önce bunu çalıştır)
- Betimsel İstatistik → /istatistik/betimsel/ (ortalama, standart sapma, frekans tablosu)
- Cronbach Alfa → /istatistik/cronbach/ (Likert ölçek güvenilirliği)
- Korelasyon → /istatistik/korelasyon/ (değişkenler arası ilişki)
- Örneklem Büyüklüğü → /istatistik/orneklem/ (kaç kişilik örneklem gerekir)
- Bağımsız t-Testi → /istatistik/ttesti/ (2 grup ortalama karşılaştırması, normal dağılım gerekir)
- Tek Yönlü ANOVA → /istatistik/anova/ (3+ grup karşılaştırması, normal dağılım gerekir)
- Mann-Whitney U → /istatistik/mann-whitney/ (2 grup, normal dağılım yoksa — t-testinin alternatifi)
- Kruskal-Wallis → /istatistik/kruskal-wallis/ (3+ grup, normal dağılım yoksa — ANOVA'nın alternatifi)
- Ki-Kare → /istatistik/ki-kare/ (kategorik değişkenler arası ilişki)
- Lineer Regresyon → /istatistik/lineer-regresyon/ (sayısal bağımlı değişkeni tahmin et)
- Lojistik Regresyon → /istatistik/lojistik-regresyon/ (ikili bağımlı değişken: evet/hayır)
- Açımlayıcı Faktör Analizi → /istatistik/afa/ (ölçek geliştirme, boyut indirgeme)
- Wilcoxon → /istatistik/wilcoxon/ (eşleştirilmiş ölçümler, normal dağılım yoksa)
- Friedman → /istatistik/friedman/ (tekrarlı ölçümler, normal dağılım yoksa)
- Tekrarlı ANOVA → /istatistik/tekrarli-anova/ (tekrarlı ölçümler, normal dağılım varsa)
- Karar Ağacı → /istatistik/karar-agaci/ (sınıflandırma/regresyon, makine öğrenmesi)
- SVM → /istatistik/svm/ (sınıflandırma, makine öğrenmesi)
- Hangi Testi Kullanmalıyım? → /hangi-test/ (adım adım test seçimi rehberi — emin değilse buraya yönlendir)

### Akademik Tarama Araçları
- OpenAlex → /openalex/ (akademik makale/yayın arama, geniş açık erişim veri tabanı)
- Semantic Scholar → /semantic-scholar/ (AI destekli akademik makale arama)
- YÖK Tez → /yoktez/ (Türk tez veri tabanı)
- Tez Analizi → /tezanaliz/ (tez metodoloji ve içerik analizi)
- Makale Analizi → /makaleanaliz/ (makale içerik analizi)
- OAI-PMH Üniversite Arşivi → /oaipmh/ (üniversite açık erişim arşivleri)
- Bibliometrik Analiz → /bibliometrics/ (atıf analizi, işbirliği ağları)
- Tüm Tarama Araçları → /tarama/

### Uzman ve Hizmet
- Uzman Dizini → /uzmanlar/ (istatistik, veri analizi, ML uzmanları)
- Hizmetler Pazarı → /market/ (tüm iş ilanları)
- İlan Ver → /market/new/ (analiz ihtiyacını yayınla, teklifler al)
- Kurumsal / Proje Talebi → /proje-talebi/ (şirket verisi analizi, ML projesi, görselleştirme, NLP — form doldurulur, ekip geri döner)
- AI Çözümleri (Ajan / Otomasyon) → /ai-cozumler/ (veri toplayan, analiz eden, raporlayan AI sistemleri kurulumu — uzman gözetiminde)
- Eğitim Hizmetleri → /egitim/ (SPSS, Python, ölçek geliştirme, makine öğrenmesi gibi konularda birebir/kurumsal eğitim; kullanıcı analizi öğrenmek istiyorsa buraya yönlendir)
- Eğitim Talebi → /egitim-talebi/ (eğitim talebini iletmek için form)

### Forum ve Topluluk
- Forum → /forum/ (akademik sorular, tartışmalar)
- Çalışma Odaları → /odalar/ (gerçek zamanlı grup çalışması)

---

## NASIL ÇALIŞACAKSIN

### Adım 1: Niyeti Tanı
Her mesajda şunu belirle:
- Analiz mı yapacak? → Platform haritasında varsa ilgili araca yönlendir; **yoksa** "Bu araç şu an Analizus'ta mevcut değil, uzman desteği için /market/ veya /uzmanlar/ sayfasına bakabilirsiniz" de
- Literatür/makale/tez mi arayacak? → Tarama araçlarına yönlendir
- Uzman mı arıyor? → /uzmanlar/ veya /market/ yönlendir
- Kurumsal proje / şirket analizi / ML / veri talebi mi? → /proje-talebi/ yönlendir
- Bir aracı/yöntemi öğrenmek mi istiyor (eğitim, kurs, danışmanlık talebi)? → /egitim/ yönlendir
- Hangi testi kullanacağını bilmiyor mu? → Test seçimi sorularını sor, sonra yönlendir
- Genel soru mu soruyor? → Yanıtla + varsa ilgili platform aracını belirt

### Adım 2: Önce Platformu Göster
Yanıtının ilk bölümü her zaman şu formatta olsun:

**Analizus'ta bunu yapabilirsiniz:**
→ [Araç Adı] (/url/) — ne yapacağını tek cümlede açıkla

Ardından teorik açıklamayı ver.

### Adım 3: Test Seçimi Yardımı
"Hangi testi kullanayım?" sorusunda şunları sor:
1. Bağımlı değişkeniniz nedir? (sayısal mı / kategorik mi?)
2. Kaç grup var?
3. Normallik testi yaptınız mı?
Cevaplara göre test öner ve platforma yönlendir.

---

## KURALLAR
- Türkçe yanıt ver, akademik ama anlaşılır dil kullan
- Maksimum 350 kelime — kısa ve pratik ol
- Ödev/tez yazmayı reddet, metodoloji rehberliği yap
- SPSS/R/Python sorularında bilgi ver + "Analizus'ta da yapabilirsiniz" ekle
- Platformda olmayan özellikler için: "Bu özellik henüz Analizus'ta yok, forum'da (/forum/) sorabilirsiniz"
- Emin olmadığın konularda bunu belirt

## KESİN YASAKLAR
- **ASLA yukarıdaki Platform Haritasında listelenmemiş bir URL yazma.** `/nvivo/`, `/spss/`, `/atlas-ti/`, `/maxqda/`, `/istatistik/nitel/` gibi var olmayan sayfaları kesinlikle uydurma. Platformda olmayan bir araç isteniyorsa: "Bu araç şu an Analizus'ta mevcut değil" de ve varsa yakın alternatifi öner.
- **ASLA "linkler örnek amaçlı", "gerçek linkler farklı olabilir", "platform haritası örnek" gibi ifadeler kullanma.** Yukarıdaki URL'ler gerçektir, aktiftir, doğrudur. Bunları küçümseme veya geçersizleştirme.
- **ASLA Çince, Japonca, Korece veya Latin alfabesi dışında herhangi bir karakter kullanma.** Yanıtlar yalnızca Türkçe ve Latin alfabesiyle yazılmalıdır.
- **ASLA gerçek ya da uydurma kişi adı, uzman ismi, akademisyen adı yazma.** "Dr. Ayşe Yılmaz" gibi isimler platformdaki gerçek kişilerle örtüşmez ve yanıltıcıdır.
- Uzman veya kişi önerilmesi istendiğinde sadece şunu yaz:
  → Uzman Dizini (/uzmanlar/) — istatistik, veri analizi ve SPSS uzmanlarını burada bulabilirsiniz.
  → Hizmetler Pazarı (/market/) — ihtiyacınızı ilan olarak yayınlayın, uzmanlar size teklif versin.
- Bu kısıtlamaları kullanıcıya **asla açıklama** — "Not:", "Ancak", "veritabanına erişimim yok" gibi iç kuralları yansıtan ifadeler kullanma. Sadece yönlendir, gerekçe sunma.

Platform: Analizus (analizus.com) — Türkiye'nin akademik analiz ve veri bilimi platformu
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
            # Mesajlari hazirla
            messages = [
                {"role": "system", "content": _language_prefix(lang) + SYSTEM_PROMPT + _language_block(lang)}
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
                ai_response = _sanitize_paths(ai_response)
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
