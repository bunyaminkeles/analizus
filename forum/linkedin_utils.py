"""
LinkedIn API Entegrasyonu
Site hesabından otomatik paylaşım için
"""
import requests
import json
from django.conf import settings
from django.core.cache import cache


class LinkedInAPI:
    """LinkedIn API wrapper for posting content"""

    AUTH_URL = "https://www.linkedin.com/oauth/v2/authorization"
    TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
    API_BASE = "https://api.linkedin.com/v2"

    def __init__(self):
        self.client_id = getattr(settings, 'LINKEDIN_CLIENT_ID', '')
        self.client_secret = getattr(settings, 'LINKEDIN_CLIENT_SECRET', '')
        self.redirect_uri = getattr(settings, 'LINKEDIN_REDIRECT_URI', '')

    def get_authorization_url(self, state='random_state'):
        """OAuth yetkilendirme URL'i oluştur"""
        scopes = 'openid profile w_member_social'
        return (
            f"{self.AUTH_URL}?"
            f"response_type=code&"
            f"client_id={self.client_id}&"
            f"redirect_uri={self.redirect_uri}&"
            f"state={state}&"
            f"scope={scopes}"
        )

    def exchange_code_for_token(self, code):
        """Authorization code'u access token'a çevir"""
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': self.redirect_uri,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        }

        response = requests.post(self.TOKEN_URL, data=data)
        if response.status_code == 200:
            return response.json()
        return None

    def get_stored_token(self):
        """Cache'den veya DB'den token al"""
        from .models import SiteSettings
        try:
            site_settings = SiteSettings.objects.first()
            if site_settings and site_settings.linkedin_access_token:
                return site_settings.linkedin_access_token
        except:
            pass
        return None

    def store_token(self, token_data):
        """Token'ı kaydet"""
        from .models import SiteSettings
        site_settings, _ = SiteSettings.objects.get_or_create(pk=1)
        site_settings.linkedin_access_token = token_data.get('access_token', '')
        site_settings.save()

    def get_user_info(self, access_token):
        """Kullanıcı bilgilerini al (person URN için)"""
        headers = {
            'Authorization': f'Bearer {access_token}',
        }
        response = requests.get(f"{self.API_BASE}/userinfo", headers=headers)
        if response.status_code == 200:
            return response.json()
        return None

    def post_share(self, text, url=None, title=None, description=None, image_url=None):
        """
        LinkedIn'e paylaşım yap

        Args:
            text: Paylaşım metni
            url: Paylaşılacak link (opsiyonel)
            title: Link başlığı (opsiyonel)
            description: Link açıklaması (opsiyonel)
            image_url: Görsel URL (opsiyonel)
        """
        access_token = self.get_stored_token()
        if not access_token:
            return {'success': False, 'error': 'Access token bulunamadı'}

        # Kullanıcı URN'ini al
        user_info = self.get_user_info(access_token)
        if not user_info:
            return {'success': False, 'error': 'Kullanıcı bilgisi alınamadı'}

        person_urn = f"urn:li:person:{user_info.get('sub')}"

        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0',
        }

        # Post body oluştur
        post_data = {
            "author": person_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": text
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }

        # Eğer URL varsa article olarak paylaş
        if url:
            post_data["specificContent"]["com.linkedin.ugc.ShareContent"]["shareMediaCategory"] = "ARTICLE"
            post_data["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [{
                "status": "READY",
                "originalUrl": url,
                "title": {
                    "text": title or "Analizus'tan Yeni İçerik"
                },
                "description": {
                    "text": description or ""
                }
            }]

            # Görsel varsa ekle
            if image_url:
                post_data["specificContent"]["com.linkedin.ugc.ShareContent"]["media"][0]["thumbnails"] = [{
                    "url": image_url
                }]

        response = requests.post(
            f"{self.API_BASE}/ugcPosts",
            headers=headers,
            json=post_data
        )

        if response.status_code in [200, 201]:
            return {'success': True, 'data': response.json()}
        else:
            return {
                'success': False,
                'error': response.text,
                'status_code': response.status_code
            }

    def share_topic(self, topic):
        """Forum konusunu LinkedIn'de paylaş"""
        text = f"🆕 Yeni Konu: {topic.subject}\n\n"
        text += f"📁 Kategori: {topic.category.title}\n"
        text += f"👤 Yazan: {topic.starter.username}\n\n"
        text += "#Analizus #VeriAnalizi #İstatistik #Akademik"

        url = f"https://www.analizus.com/topic/{topic.pk}/"

        return self.post_share(
            text=text,
            url=url,
            title=topic.subject,
            description=f"{topic.category.title} kategorisinde yeni tartışma"
        )

    def share_job(self, job):
        """İş ilanını LinkedIn'de paylaş"""
        text = f"💼 Yeni İş İlanı: {job.title}\n\n"
        text += f"💰 Bütçe: ₺{job.budget_min} - ₺{job.budget_max}\n"
        text += f"📊 Kategori: {job.category.title}\n\n"
        text += "Detaylar ve başvuru için linke tıklayın.\n\n"
        text += "#Analizus #Freelance #VeriAnalizi #İşİlanı"

        url = f"https://www.analizus.com/market/job/{job.pk}/"

        return self.post_share(
            text=text,
            url=url,
            title=job.title,
            description=f"Bütçe: ₺{job.budget_min} - ₺{job.budget_max}"
        )

    def share_custom(self, text, url=None):
        """Özel içerik paylaş"""
        return self.post_share(text=text, url=url)


# Singleton instance
linkedin_api = LinkedInAPI()
