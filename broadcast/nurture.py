"""Sayfa gezintisine göre otomatik tetiklenen öneri (nurture) e-postası.

Segmentasyon: son WINDOW_DAYS gün içinde (takvim gününe kısıtlı değil) 2+
farklı analiz/tarama aracı ziyaret eden, onay vermiş kullanıcılar. Gönderim
`forum.api_views.cron_send_nurture_emails` tarafından günlük tetiklenir.
"""
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.postgres.aggregates import ArrayAgg
from django.core.mail import send_mail
from django.db.models import Count, Max
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.html import strip_tags

from analytics.models import PageView
from analytics.utils import _SLUG_TO_NAME

from .models import NurtureEmailLog

MIN_DISTINCT_TOOLS = 2
WINDOW_DAYS = 3
COOLDOWN_DAYS = 14

ALLOWED_TAB_NAMES = {f'Analiz: {name}' for name in _SLUG_TO_NAME.values()} | {
    'OpenAlex', 'PubMed', 'Semantic Scholar', 'TR Dizin', 'YÖK Tez', 'OAI-PMH',
}


def _display_label(tab_name):
    return tab_name[len('Analiz: '):] if tab_name.startswith('Analiz: ') else tab_name


def _site_url(url_name, *args):
    base = getattr(settings, 'SITE_URL', 'http://localhost:8000').rstrip('/')
    return base + reverse(url_name, args=args)


def get_daily_candidates(run_date):
    """`run_date`'den önceki WINDOW_DAYS günlük kayan pencerede (dün dahil,
    bugün hariç) 2+ farklı araç ziyaret eden, onaylı ve cooldown dışındaki
    kullanıcıları döner: [{'user_id', 'tool_labels': [...], 'last_visit_date'}]
    """
    window_start = run_date - timedelta(days=WINDOW_DAYS)
    window_end = run_date - timedelta(days=1)

    rows = list(
        PageView.objects
        .filter(
            timestamp__date__gte=window_start,
            timestamp__date__lte=window_end,
            tab_name__in=ALLOWED_TAB_NAMES,
            user__profile__marketing_email_consent=True,
            user__profile__preferred_language='tr',
        )
        .values('user_id')
        .annotate(
            tool_count=Count('tab_name', distinct=True),
            last_visit=Max('timestamp'),
            tool_names=ArrayAgg('tab_name', distinct=True),
        )
        .filter(tool_count__gte=MIN_DISTINCT_TOOLS)
    )
    if not rows:
        return []

    cooldown_cutoff = timezone.now() - timedelta(days=COOLDOWN_DAYS)
    recently_sent_user_ids = set(
        NurtureEmailLog.objects
        .filter(user_id__in=[r['user_id'] for r in rows], sent_at__gte=cooldown_cutoff)
        .values_list('user_id', flat=True)
    )

    candidates = []
    for row in rows:
        if row['user_id'] in recently_sent_user_ids:
            continue
        candidates.append({
            'user_id': row['user_id'],
            'tool_labels': [_display_label(t) for t in row['tool_names']],
            'last_visit_date': row['last_visit'].date(),
        })
    return candidates


def build_email(tool_labels):
    """(subject, body) döner. body, [isim](url) sözdizimi içerir — gönderimde
    `forum/emails/admin_broadcast.html` ile aynen render edilir."""
    if len(tool_labels) == 1:
        tool_text = tool_labels[0]
    else:
        tool_text = ', '.join(tool_labels[:-1]) + ' ve ' + tool_labels[-1]

    subject = 'Aynı Analizi Siz de mi Tekrar Tekrar Kontrol Ediyorsunuz?'
    bunyamin_url = _site_url('profile_detail', 'bunyamin')
    joseph_url = _site_url('profile_detail', 'joseph')
    uzmanlar_url = _site_url('uzman_dizini')

    body = (
        f"Son günlerde Analizus'ta {tool_text} sayfalarına birden fazla kez "
        "döndüğünüzü fark ettik.\n\n"
        "Bu genellikle iyi bir işaret: yöntemi doğru kurmak, sonucundan emin "
        "olmak isteyen birinin izi. Ama tam o noktada tek başına ilerlemek "
        "zorlaşabilir.\n\n"
        "Böyle anlar için bir uzmanla birebir çalışabilirsiniz:\n\n"
        f"[Bünyamin]({bunyamin_url})\n"
        f"[Joseph]({joseph_url})\n\n"
        "Ya da tüm uzmanlar arasından size en uygun olanı kendiniz seçin:\n"
        f"[Tüm Uzmanlar]({uzmanlar_url})\n\n"
        "Analizinizin sonuna az kaldıysa, son adımı birlikte atmak ister "
        "misiniz?\n\n"
        "Analizus Ekibi"
    )
    return subject, body


def send_nurture_emails(run_date=None):
    """Günlük cron tarafından çağrılır. Döner: {'sent', 'failed', 'candidates'}."""
    run_date = run_date or timezone.localdate()
    candidates = get_daily_candidates(run_date)
    if not candidates:
        return {'sent': 0, 'failed': 0, 'candidates': 0}

    users_by_id = {
        u.id: u for u in User.objects.filter(
            id__in=[c['user_id'] for c in candidates]
        ).exclude(email='')
    }

    sent = failed = 0
    for candidate in candidates:
        user = users_by_id.get(candidate['user_id'])
        if not user:
            continue

        subject, body = build_email(candidate['tool_labels'])
        html_message = render_to_string('forum/emails/admin_broadcast.html', {
            'subject': subject,
            'body': body,
            'site_name': 'Analizus',
        })
        plain_message = strip_tags(body)

        try:
            send_mail(
                subject, plain_message, settings.DEFAULT_FROM_EMAIL, [user.email],
                html_message=html_message, fail_silently=False,
            )
            sent += 1
        except Exception:
            failed += 1
            continue

        NurtureEmailLog.objects.create(
            user=user,
            trigger_date=candidate['last_visit_date'],
            tool_labels=', '.join(candidate['tool_labels']),
        )

    return {'sent': sent, 'failed': failed, 'candidates': len(candidates)}
