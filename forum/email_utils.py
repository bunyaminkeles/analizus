"""
E-posta bildirim yardımcıları
"""
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone as tz
import threading
import logging

logger = logging.getLogger(__name__)


def send_email_async(subject, message, recipient_list, html_message=None):
    """
    Django'nun send_mail fonksiyonunu kullanarak arka planda e-posta gönderir.
    """
    def _send():
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                recipient_list,
                fail_silently=False,
                html_message=html_message
            )
            for recipient in recipient_list:
                logger.info(f"E-posta başarıyla gönderildi: {recipient}")
        except Exception as e:
            logger.error(f"E-posta gönderim hatası: {e}")

    thread = threading.Thread(target=_send, daemon=True)
    thread.start()


def send_proposal_notification(proposal):
    """Yeni teklif geldiğinde ilan sahibine email gönderir"""
    job = proposal.job
    owner = job.owner
    if not owner.email:
        return

    site = getattr(settings, 'SITE_URL', 'https://www.analizus.com')
    subject = f"İlanınıza yeni bir teklif geldi: {job.title}"
    message = f"""Merhaba {owner.username},

"{job.title}" ilanınıza {proposal.expert.username} teklif verdi!

Teklif: {proposal.price} TL
Süre: {proposal.duration}
Ön Yazı: {proposal.message[:300]}

Teklifi görmek ve değerlendirmek için:
{site}/jobs/{job.pk}/

---
Bu bir otomatik bildirimdir.
Analizus - Akademik Veri Üssü"""

    send_email_async(subject, message, [owner.email])


def send_topic_reply_notification(post, topic):
    """Bir konuya cevap yazıldığında konu sahibine email gönderir"""
    if post.created_by == topic.starter:
        return
    if not topic.starter.email:
        return
    if hasattr(topic.starter, 'profile') and not topic.starter.profile.email_on_reply:
        return

    subject = f"{post.created_by.username} konunuza cevap yazdı: {topic.subject}"
    message = f"""Merhaba {topic.starter.username},

"{topic.subject}" başlıklı konunuza yeni bir cevap geldi!

Cevap Yazan: {post.created_by.username}
Mesaj: {post.message[:200]}...

Cevabın tamamını görmek için:
https://analizus.com/topic/{topic.pk}/

---
Bu bir otomatik bildirimdir.
Analizus - Akademik Veri Üssü"""

    send_email_async(subject, message, [topic.starter.email])


def send_private_message_notification(sender, receiver, message_content):
    """Özel mesaj geldiğinde alıcıya email gönderir"""
    if not receiver.email:
        return
    if hasattr(receiver, 'profile') and not receiver.profile.email_on_private_message:
        return

    subject = f"{sender.username} size özel mesaj gönderdi"
    message = f"""Merhaba {receiver.username},

{sender.username} size yeni bir özel mesaj gönderdi!

Mesaj İçeriği:
{message_content[:300]}...

Mesajı okumak ve cevaplamak için:
https://analizus.com/inbox/

---
Bu bir otomatik bildirimdir.
Analizus - Akademik Veri Üssü"""

    send_email_async(subject, message, [receiver.email])


def send_mention_notification(mentioned_user, post, topic):
    """Bir mesajda @mention edildiğinde kullanıcıya email gönderir"""
    if not mentioned_user.email:
        return

    subject = f"{post.created_by.username} sizi bir tartışmada etiketledi"
    message = f"""Merhaba {mentioned_user.username},

{post.created_by.username} sizi "{topic.subject}" konusunda etiketledi!

Konuya gitmek için:
https://analizus.com/topic/{topic.pk}/

---
Analizus - Akademik Veri Üssü"""

    send_email_async(subject, message, [mentioned_user.email])


# ═══════════════════════════════════════════════════════════════════════════
# ADMİN BİLDİRİM SİSTEMİ
# ═══════════════════════════════════════════════════════════════════════════

# Olay renkleri
_COLORS = {
    'user':      '#22c55e',   # yeşil  — yeni üye
    'topic':     '#3b82f6',   # mavi   — forum konusu
    'post':      '#8b5cf6',   # mor    — forum cevabı
    'job':       '#f97316',   # turuncu — iş ilanı
    'proposal':  '#eab308',   # sarı   — teklif
    'accepted':  '#10b981',   # zümrüt — teklif kabul
    'completed': '#6366f1',   # indigo — iş tamamlandı
    'blog':      '#06b6d4',   # cyan   — blog yazısı
    'analysis':  '#a855f7',   # viyole — analiz
}


def _build_admin_html(event_label: str, color: str, title: str, rows: list[tuple], url: str, button_text: str) -> str:
    """
    Tutarlı görünümlü admin bildirim HTML'i üretir.
    rows: [(label, value), ...] listesi
    """
    rows_html = ''.join(
        f'<tr>'
        f'<td style="padding:8px 12px;color:#94a3b8;font-size:13px;width:38%;border-bottom:1px solid #334155;">{label}</td>'
        f'<td style="padding:8px 12px;color:#e2e8f0;font-size:13px;font-weight:500;border-bottom:1px solid #334155;">{value}</td>'
        f'</tr>'
        for label, value in rows
    )
    now_str = tz.now().strftime('%d.%m.%Y %H:%M')
    return f"""<!DOCTYPE html>
<html lang="tr">
<body style="margin:0;padding:0;background:#0f172a;font-family:Arial,Helvetica,sans-serif;">
<div style="max-width:580px;margin:0 auto;padding:28px 16px;">

  <div style="text-align:center;margin-bottom:24px;">
    <span style="font-size:24px;font-weight:800;color:#6366f1;letter-spacing:-1px;">Analizus</span>
    <span style="color:#475569;font-size:13px;margin-left:8px;">| Admin Bildirimi</span>
  </div>

  <div style="background:#1e293b;border-radius:14px;padding:24px 24px 20px;border-left:4px solid {color};">
    <span style="display:inline-block;background:{color}22;color:{color};font-size:11px;font-weight:700;
      padding:4px 12px;border-radius:20px;text-transform:uppercase;letter-spacing:1px;margin-bottom:12px;">
      {event_label}
    </span>
    <h2 style="margin:0 0 18px;color:#f1f5f9;font-size:17px;font-weight:600;line-height:1.4;">{title}</h2>

    <table style="width:100%;border-collapse:collapse;background:#0f172a;border-radius:8px;overflow:hidden;">
      {rows_html}
    </table>

    <a href="{url}"
       style="display:inline-block;margin-top:20px;padding:10px 24px;background:{color};
              color:#fff;text-decoration:none;border-radius:8px;font-weight:600;font-size:14px;">
      {button_text} →
    </a>
  </div>

  <div style="text-align:center;margin-top:18px;color:#334155;font-size:12px;">
    Analizus Admin Bildirimi &nbsp;·&nbsp; {now_str}
  </div>
</div>
</body>
</html>"""


def _send_admin(subject: str, html: str, plain: str):
    """Admin bildirim e-postasını arka planda gönderir."""
    admin_email = getattr(settings, 'ADMIN_NOTIFICATION_EMAIL', None)
    if not admin_email:
        return
    send_email_async(subject, plain, [admin_email], html_message=html)


# ── Olay bazlı yardımcılar ──────────────────────────────────────────────

def notify_admin_new_user(user):
    """Yeni kullanıcı kaydı admin bildirimi"""
    try:
        site = getattr(settings, 'SITE_URL', 'https://www.analizus.com')
        color = _COLORS['user']
        rows = [
            ('Kullanıcı adı', user.username),
            ('E-posta', user.email or '—'),
            ('Ad Soyad', f"{user.first_name} {user.last_name}".strip() or '—'),
            ('Kayıt tarihi', user.date_joined.strftime('%d.%m.%Y %H:%M')),
        ]
        html = _build_admin_html(
            '🟢 Yeni Üye', color,
            f"{user.username} platforma katıldı",
            rows,
            f"{site}/admin/auth/user/{user.pk}/change/",
            'Admin Panelde Görüntüle'
        )
        plain = f"Yeni üye: {user.username} ({user.email}) — {user.date_joined.strftime('%d.%m.%Y %H:%M')}"
        _send_admin(f"[Analizus] Yeni Üye: {user.username}", html, plain)
    except Exception as e:
        logger.error(f"Admin yeni üye bildirimi gönderilemedi: {e}")


def notify_admin_new_topic(topic):
    """Yeni forum konusu admin bildirimi"""
    try:
        site = getattr(settings, 'SITE_URL', 'https://www.analizus.com')
        color = _COLORS['topic']
        rows = [
            ('Başlık', topic.subject),
            ('Kategori', str(topic.category)),
            ('Yazan', topic.starter.username),
            ('Tarih', topic.created_at.strftime('%d.%m.%Y %H:%M')),
        ]
        html = _build_admin_html(
            '🔵 Yeni Forum Konusu', color,
            topic.subject,
            rows,
            f"{site}{topic.get_absolute_url()}",
            'Konuya Git'
        )
        plain = f"Yeni konu: '{topic.subject}' — {topic.starter.username} ({topic.category})"
        _send_admin(f"[Analizus] Yeni Konu: {topic.subject[:60]}", html, plain)
    except Exception as e:
        logger.error(f"Admin yeni konu bildirimi gönderilemedi: {e}")


def notify_admin_new_post(post):
    """Yeni forum cevabı admin bildirimi"""
    try:
        site = getattr(settings, 'SITE_URL', 'https://www.analizus.com')
        color = _COLORS['post']
        preview = post.message[:200] + ('…' if len(post.message) > 200 else '')
        rows = [
            ('Konu', post.topic.subject),
            ('Cevaplayan', post.created_by.username),
            ('Mesaj önizleme', preview),
            ('Tarih', post.created_at.strftime('%d.%m.%Y %H:%M')),
        ]
        html = _build_admin_html(
            '🟣 Yeni Forum Cevabı', color,
            f'{post.created_by.username} cevap yazdı: “{post.topic.subject}”',
            rows,
            f"{site}{post.get_absolute_url()}",
            'Cevaba Git'
        )
        plain = f"Yeni cevap: {post.created_by.username} → '{post.topic.subject}'"
        _send_admin(f"[Analizus] Yeni Cevap: {post.topic.subject[:55]}", html, plain)
    except Exception as e:
        logger.error(f"Admin yeni cevap bildirimi gönderilemedi: {e}")


def notify_admin_new_job(job):
    """Yeni iş ilanı admin bildirimi"""
    try:
        site = getattr(settings, 'SITE_URL', 'https://www.analizus.com')
        color = _COLORS['job']
        rows = [
            ('İlan başlığı', job.title),
            ('İlan sahibi', job.owner.username),
            ('Bütçe', f"Maks. {job.budget_max} TL"),
            ('Kategori', str(job.category) if job.category else '—'),
            ('Referans', job.reference_number or '—'),
            ('Tarih', job.created_at.strftime('%d.%m.%Y %H:%M')),
        ]
        html = _build_admin_html(
            '🟠 Yeni İş İlanı', color,
            job.title,
            rows,
            f"{site}/jobs/{job.pk}/",
            'İlana Git'
        )
        plain = f"Yeni ilan: '{job.title}' — {job.owner.username} (Maks. {job.budget_max} TL)"
        _send_admin(f"[Analizus] Yeni İlan: {job.title[:60]}", html, plain)
    except Exception as e:
        logger.error(f"Admin yeni ilan bildirimi gönderilemedi: {e}")


def notify_admin_new_proposal(proposal):
    """Yeni teklif admin bildirimi"""
    try:
        site = getattr(settings, 'SITE_URL', 'https://www.analizus.com')
        color = _COLORS['proposal']
        preview = proposal.message[:200] + ('…' if len(proposal.message) > 200 else '')
        rows = [
            ('İlan', proposal.job.title),
            ('İlan sahibi', proposal.job.owner.username),
            ('Teklif veren', proposal.expert.username),
            ('Fiyat', f"{proposal.price} TL"),
            ('Süre', proposal.duration),
            ('Ön yazı', preview),
            ('Tarih', proposal.created_at.strftime('%d.%m.%Y %H:%M')),
        ]
        html = _build_admin_html(
            '🟡 Yeni Teklif', color,
            f'{proposal.expert.username} teklif verdi: "{proposal.job.title}"',
            rows,
            f"{site}/admin/forum/jobproposal/{proposal.pk}/change/",
            'Teklifi Görüntüle'
        )
        plain = f"Yeni teklif: {proposal.expert.username} → '{proposal.job.title}' — {proposal.price} TL"
        _send_admin(f"[Analizus] Yeni Teklif: {proposal.job.title[:55]}", html, plain)
    except Exception as e:
        logger.error(f"Admin yeni teklif bildirimi gönderilemedi: {e}")


def notify_admin_proposal_accepted(proposal):
    """Teklif kabul edildi admin bildirimi"""
    try:
        site = getattr(settings, 'SITE_URL', 'https://www.analizus.com')
        color = _COLORS['accepted']
        rows = [
            ('İlan', proposal.job.title),
            ('İlan sahibi', proposal.job.owner.username),
            ('Kabul edilen uzman', proposal.expert.username),
            ('Anlaşılan fiyat', f"{proposal.price} TL"),
            ('Süre', proposal.duration),
        ]
        html = _build_admin_html(
            '✅ Teklif Kabul Edildi', color,
            f'"{proposal.job.title}" ilanında anlaşma sağlandı',
            rows,
            f"{site}/jobs/{proposal.job.pk}/",
            'İlana Git'
        )
        plain = f"Teklif kabul: '{proposal.job.title}' — uzman: {proposal.expert.username} ({proposal.price} TL)"
        _send_admin(f"[Analizus] ✅ Teklif Kabul: {proposal.job.title[:50]}", html, plain)
    except Exception as e:
        logger.error(f"Admin teklif kabul bildirimi gönderilemedi: {e}")


def notify_admin_job_completed(job):
    """İş ilanı tamamlandı admin bildirimi"""
    try:
        site = getattr(settings, 'SITE_URL', 'https://www.analizus.com')
        color = _COLORS['completed']
        accepted = job.proposals.filter(status='accepted').first()
        expert_name = accepted.expert.username if accepted else '—'
        rows = [
            ('İlan', job.title),
            ('İlan sahibi', job.owner.username),
            ('Uzman', expert_name),
            ('Referans', job.reference_number or '—'),
        ]
        html = _build_admin_html(
            '⭐ İş Tamamlandı', color,
            f'"{job.title}" başarıyla tamamlandı',
            rows,
            f"{site}/admin/forum/freelancejob/{job.pk}/change/",
            'İlanı Görüntüle'
        )
        plain = f"İş tamamlandı: '{job.title}' — {job.owner.username} & {expert_name}"
        _send_admin(f"[Analizus] ⭐ İş Tamamlandı: {job.title[:50]}", html, plain)
    except Exception as e:
        logger.error(f"Admin iş tamamlandı bildirimi gönderilemedi: {e}")


def notify_admin_blog_published(blog_post):
    """Blog yazısı yayınlandı admin bildirimi"""
    try:
        site = getattr(settings, 'SITE_URL', 'https://www.analizus.com')
        color = _COLORS['blog']
        rows = [
            ('Başlık', blog_post.title),
            ('Yazar', blog_post.author.username),
            ('Kategori', str(blog_post.category) if blog_post.category else '—'),
            ('URL', f"{site}{blog_post.get_absolute_url()}"),
        ]
        html = _build_admin_html(
            '📝 Blog Yazısı Yayınlandı', color,
            blog_post.title,
            rows,
            f"{site}{blog_post.get_absolute_url()}",
            'Blog Yazısını Görüntüle'
        )
        plain = f"Blog yayınlandı: '{blog_post.title}' — {blog_post.author.username}"
        _send_admin(f"[Analizus] 📝 Blog: {blog_post.title[:60]}", html, plain)
    except Exception as e:
        logger.error(f"Admin blog bildirimi gönderilemedi: {e}")


def notify_admin_analysis_completed(job):
    """İstatistik analizi tamamlandı admin bildirimi"""
    try:
        if not job.user:
            return
        site = getattr(settings, 'SITE_URL', 'https://www.analizus.com')
        color = _COLORS['analysis']
        tool_names = {
            'cronbach': 'Cronbach Alpha', 'normallik': 'Normallik Testi',
            'betimsel': 'Betimsel İstatistik', 'korelasyon': 'Korelasyon Matrisi',
            'ttesti': 't-Testi', 'anova': 'ANOVA',
            'mann_whitney': 'Mann-Whitney U', 'kruskal_wallis': 'Kruskal-Wallis',
            'ki_kare': 'Ki-Kare', 'lineer_regresyon': 'Çoklu Doğrusal Regresyon',
            'lojistik_regresyon': 'Lojistik Regresyon',
        }
        tool_urls = {
            'cronbach': 'cronbach/', 'normallik': 'normallik/',
            'betimsel': 'betimsel/', 'korelasyon': 'korelasyon/',
            'ttesti': 'ttesti/', 'anova': 'anova/',
            'mann_whitney': 'mann-whitney/', 'kruskal_wallis': 'kruskal-wallis/',
            'ki_kare': 'ki-kare/', 'lineer_regresyon': 'lineer-regresyon/',
            'lojistik_regresyon': 'lojistik-regresyon/',
        }
        tool_label = tool_names.get(job.tool, job.tool)
        tool_path = tool_urls.get(job.tool, '')
        rows = [
            ('Araç', tool_label),
            ('Kullanıcı', job.user.username),
            ('Durum', job.status),
            ('Tarih', job.updated_at.strftime('%d.%m.%Y %H:%M') if hasattr(job, 'updated_at') else '—'),
        ]
        html = _build_admin_html(
            '📊 Analiz Tamamlandı', color,
            f"{job.user.username} — {tool_label}",
            rows,
            f"{site}/istatistik/{tool_path}",
            'Analiz Sayfasına Git'
        )
        plain = f"Analiz tamamlandı: {tool_label} — kullanıcı: {job.user.username}"
        _send_admin(f"[Analizus] 📊 Analiz: {tool_label} ({job.user.username})", html, plain)
    except Exception as e:
        logger.error(f"Admin analiz bildirimi gönderilemedi: {e}")
