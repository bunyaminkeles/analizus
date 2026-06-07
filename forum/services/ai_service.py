"""
Analizus AI Asistan Servisi
Groq API entegrasyonu (Llama 3 modeli)
"""
import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Sen Analizus platformunun özel AI asistanısın. Görevin yalnızca genel bilgi vermek değil — kullanıcının ne yapmak istediğini anlayıp onu Analizus platformundaki doğru araca, sayfaya veya hizmete yönlendirmektir.

## PLATFORM HARİTASI

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

### Forum ve Topluluk
- Forum → /forum/ (akademik sorular, tartışmalar)
- Çalışma Odaları → /odalar/ (gerçek zamanlı grup çalışması)

---

## NASIL ÇALIŞACAKSIN

### Adım 1: Niyeti Tanı
Her mesajda şunu belirle:
- Analiz mı yapacak? → İlgili istatistik aracına yönlendir
- Literatür/makale/tez mi arayacak? → Tarama araçlarına yönlendir
- Uzman mı arıyor? → /uzmanlar/ veya /market/ yönlendir
- Hangi testi kullanacağını bilmiyor mu? → Test seçimi sorularını sor, sonra yönlendir
- Genel soru mu soruyor? → Yanıtla + varsa ilgili platfom aracını belirt

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
- **ASLA gerçek ya da uydurma kişi adı, uzman ismi, akademisyen adı yazma.** "Dr. Ayşe Yılmaz" gibi isimler platformdaki gerçek kişilerle örtüşmez ve yanıltıcıdır.
- Uzman veya kişi önerilmesi istendiğinde sadece şunu yaz:
  → Uzman Dizini (/uzmanlar/) — istatistik, veri analizi ve SPSS uzmanlarını burada bulabilirsiniz.
  → Hizmetler Pazarı (/market/) — ihtiyacınızı ilan olarak yayınlayın, uzmanlar size teklif versin.
- Platform veritabanına erişimin yok; kimin uzman olduğunu bilemezsin — sadece yönlendir.

Platform: Analizus (analizus.com) — Türkiye'nin akademik analiz ve veri bilimi platformu
"""


class GroqService:
    """Groq AI servisi (Llama 3)"""

    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "llama-3.3-70b-versatile"

    def is_available(self):
        """Servis kullanılabilir mi?"""
        return bool(self.api_key)

    def generate_response(self, user_message: str, context: str = None) -> dict:
        """
        Kullanıcı mesajına yanıt üret

        Args:
            user_message: Kullanıcının sorusu
            context: Ek bağlam (opsiyonel)

        Returns:
            dict: {'success': bool, 'response': str, 'error': str}
        """
        if not self.is_available():
            return {
                'success': False,
                'response': None,
                'error': 'AI servisi şu anda kullanılamıyor.'
            }

        try:
            # Mesajları hazırla
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT}
            ]

            if context:
                messages.append({"role": "user", "content": f"Bağlam:\n{context}"})

            messages.append({"role": "user", "content": user_message})

            # API isteği
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
                return {
                    'success': True,
                    'response': ai_response,
                    'error': None
                }
            else:
                error_msg = response.json().get('error', {}).get('message', 'Bilinmeyen hata')
                logger.error(f"Groq API hatası: {response.status_code} - {error_msg}")
                return {
                    'success': False,
                    'response': None,
                    'error': f'API hatası: {error_msg}'
                }

        except requests.Timeout:
            return {
                'success': False,
                'response': None,
                'error': 'İstek zaman aşımına uğradı. Lütfen tekrar deneyin.'
            }
        except Exception as e:
            logger.error(f"Groq API hatası: {e}")
            return {
                'success': False,
                'response': None,
                'error': f'Bir hata oluştu: {str(e)}'
            }

    def suggest_answer(self, topic_subject: str, topic_content: str) -> dict:
        """
        Forum konusu için yanıt önerisi üret

        Args:
            topic_subject: Konu başlığı
            topic_content: Konu içeriği

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
