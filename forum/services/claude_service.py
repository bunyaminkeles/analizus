"""
Analizus AI Yorumu Servisi
Anthropic Claude entegrasyonu — tarama/analiz sonuçlarına ücretsiz AI özeti.
Mevcut AI Asistan (GroqService, ai_service.py) ile karıştırılmamalı: o genel
sohbet asistanı, bu servis yalnızca tek seferlik, araca özel sonuç yorumu üretir.
"""
import logging

from django.conf import settings

logger = logging.getLogger(__name__)

_LANGUAGE_NAMES = {'tr': 'Türkçe', 'en': 'English', 'de': 'Deutsch'}

MODEL = "claude-haiku-5-5"
MAX_TOKENS = 512


class ClaudeSummaryService:
    """Tarama/analiz sonuçlarına Claude ile ücretsiz AI yorumu üretir."""

    def __init__(self):
        self.api_key = settings.ANTHROPIC_API_KEY
        self._client = None

    def is_available(self):
        return bool(self.api_key)

    def _get_client(self):
        if self._client is None:
            import anthropic
            self._client = anthropic.Anthropic(api_key=self.api_key)
        return self._client

    def generate_summary(self, tool: str, prompt: str, lang: str = 'tr') -> dict:
        """
        Args:
            tool: çağıran araç adı (yalnız log/hata mesajları için, örn. 'istatistik')
            prompt: araca özel, sonuç verisini içeren hazır kullanıcı mesajı
            lang: kullanıcı arayüz dili (tr/en/de)

        Returns:
            dict: {'success', 'text', 'input_tokens', 'output_tokens', 'error'}
            Hata durumunda exception fırlatmaz — çağıran taraf job'u bu yüzden
            düşürmemeli, yalnızca AI yorumunu boş bırakmalı.
        """
        if not self.is_available():
            return {'success': False, 'text': None, 'input_tokens': 0,
                     'output_tokens': 0, 'error': 'ANTHROPIC_API_KEY tanımlı değil'}

        language_name = _LANGUAGE_NAMES.get(lang, 'Türkçe')
        system_prompt = (
            "Sen Analizus akademik analiz platformunun istatistik/literatür danışmanısın. "
            "Sana verilen analiz/tarama sonucunu akademik dile uygun, kısa ve anlaşılır şekilde yorumla. "
            "Abartılı veya kesin iddialarda bulunma, yalnızca verilen sonucu yansıt; resmi kurum "
            "izlenimi verme. En fazla 120 kelime yaz, doğrudan yorumla başla (giriş cümlesi kurma). "
            f"Yanıtının tamamını {language_name} dilinde yaz."
        )

        try:
            response = self._get_client().messages.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                system=system_prompt,
                messages=[{"role": "user", "content": prompt}],
            )
            text = "".join(
                block.text for block in response.content if getattr(block, "type", None) == "text"
            ).strip()
            usage = getattr(response, "usage", None)
            return {
                'success': True,
                'text': text or None,
                'input_tokens': getattr(usage, 'input_tokens', 0) or 0,
                'output_tokens': getattr(usage, 'output_tokens', 0) or 0,
                'error': None,
            }
        except Exception as e:
            logger.error(f"Claude AI özet hatası ({tool}): {e}")
            return {'success': False, 'text': None, 'input_tokens': 0,
                     'output_tokens': 0, 'error': str(e)}


# Singleton instance
claude_summary_service = ClaudeSummaryService()
