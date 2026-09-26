from django import template
from django.utils.safestring import mark_safe
from django.utils.html import escape
from django.utils.translation import pgettext, pgettext_lazy
from forum.mention_utils import render_mentions_html

register = template.Library()


# Rütbe bilgileri: (rütbe_key): (isim, renk, ikon, css_class)
# İsimler Profile.RANK_CHOICES ile aynı msgid — tek çeviri
RANK_INFO = {
    'newbie': (pgettext_lazy('rütbe', 'Çaylak'), '#94a3b8', '🌱', 'secondary'),
    'member': (pgettext_lazy('rütbe', 'Üye'), '#64748b', '👤', 'secondary'),
    'active': (pgettext_lazy('rütbe', 'Aktif Üye'), '#3b82f6', '⚡', 'info'),
    'contributor': (pgettext_lazy('rütbe', 'Katkıcı'), '#8b5cf6', '✍️', 'primary'),
    'expert': (pgettext_lazy('rütbe', 'Uzman'), '#f59e0b', '🎯', 'warning'),
    'master': (pgettext_lazy('rütbe', 'Usta'), '#ef4444', '👑', 'danger'),
    'legend': (pgettext_lazy('rütbe', 'Efsane'), '#eab308', '🏆', 'warning'),
    'admin': (pgettext_lazy('rütbe', 'Yönetici'), '#dc2626', '🛡️', 'danger'),
}


@register.filter
def get_user_rank(user):
    """
    Kullanıcının rütbesini ve CSS bilgilerini döndürür.
    Döndüreceği format: (Rütbe Adı, CSS Class'ı, İkon)
    """
    if not user.is_authenticated:
        return pgettext('rütbe', 'Ziyaretçi'), "secondary", "bi-person"

    if not hasattr(user, 'profile'):
        return pgettext('rütbe', 'Çaylak'), "secondary", "🌱"

    rank = user.profile.rank
    info = RANK_INFO.get(rank, RANK_INFO['newbie'])
    return info[0], info[3], info[2]


@register.filter
def get_rank_badge(user):
    """Kullanıcının rütbe badge'ini HTML olarak döndürür"""
    if not user.is_authenticated:
        return mark_safe('<span class="badge bg-secondary">%s</span>' % escape(pgettext('rütbe', 'Ziyaretçi')))

    if not hasattr(user, 'profile'):
        return mark_safe('<span class="badge bg-secondary">🌱 %s</span>' % escape(pgettext('rütbe', 'Çaylak')))

    rank = user.profile.rank
    info = RANK_INFO.get(rank, RANK_INFO['newbie'])
    name, color, icon, css = info

    return mark_safe(f'<span class="badge" style="background-color: {color};">{icon} {escape(name)}</span>')


@register.filter
def get_user_badges(user, limit=3):
    """Kullanıcının rozetlerini döndürür"""
    if not user.is_authenticated or not hasattr(user, 'profile'):
        return []
    return user.profile.badges.all()[:limit]


@register.simple_tag
def render_badge(badge):
    """Rozeti HTML olarak render eder"""
    return mark_safe(
        f'<span class="badge me-1" style="background-color: {badge.color};" '
        f'title="{escape(badge.localized_description)}">'
        f'<i class="{badge.icon}"></i> {escape(badge.localized_name)}</span>'
    )


@register.simple_tag
def render_user_badges(user, limit=3):
    """Kullanıcının rozetlerini HTML olarak render eder"""
    if not user.is_authenticated or not hasattr(user, 'profile'):
        return ''

    badges = user.profile.badges.all()[:limit]
    if not badges:
        return ''

    html_parts = []
    for badge in badges:
        html_parts.append(
            f'<span class="badge me-1" style="background-color: {badge.color}; font-size: 0.7rem;" '
            f'title="{escape(badge.localized_description)}">'
            f'<i class="{badge.icon}"></i></span>'
        )

    extra_count = user.profile.badges.count() - limit
    if extra_count > 0:
        html_parts.append(f'<span class="text-muted small">+{extra_count}</span>')

    return mark_safe(''.join(html_parts))


@register.filter(needs_autoescape=True)
def render_mentions(value, autoescape=True):
    """@username kalıplarını tıklanabilir profil linklerine dönüştürür"""
    if autoescape:
        value = escape(value)
    return mark_safe(render_mentions_html(value))


@register.filter
def reputation_display(user):
    """Kullanıcının puanını formatlı gösterir"""
    if not user.is_authenticated or not hasattr(user, 'profile'):
        return "0"

    rep = user.profile.reputation
    if rep >= 1000:
        return f"{rep / 1000:.1f}K"
    return str(rep)

@register.simple_tag
def get_team_members():
    """Aktif ekip üyelerini sıralamalarına göre getirir"""
    from forum.models import TeamMember
    return TeamMember.objects.filter(is_active=True).order_by('order')