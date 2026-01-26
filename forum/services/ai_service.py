"""
Analizus AI Asistan Servisi
Groq API entegrasyonu (Llama 3 modeli)
"""
import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# Sistem promptu - Akademik asistan rolü
SYSTEM_PROMPT = """Sen Analizus platformunun AI asistanısın. Akademik araştırma, istatistik analizi ve veri bilimi konularında uzman bir yardımcısın.

Görevlerin:
1. SPSS, Python, R Studio ile ilgili istatistik sorularını yanıtla
2. Akademik araştırma metodolojisi hakkında rehberlik et
3. Veri analizi yöntemlerini açıkla (t-test, ANOVA, regresyon vb.)
4. Tez yazım sürecinde destek ol
5. Akademik yazım kurallarını açıkla

Kurallar:
- Türkçe yanıt ver
- Kısa ve öz ol (maksimum 500 kelime)
- Kod örnekleri verirken açıklayıcı ol
- Akademik etik kurallarına uygun davran
- Ödev/tez yazmaktan kaçın, sadece yönlendirme yap
- Emin olmadığın konularda bunu belirt

Platform: Analizus - Akademik Analiz ve Veri Bilimi Topluluğu
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
