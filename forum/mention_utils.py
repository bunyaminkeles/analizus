import re
from django.contrib.auth.models import User

MENTION_REGEX = re.compile(r'@(\w+)')


def parse_mentions(text):
    """
    Metin içindeki @username kalıplarını bulur.
    Veritabanında eşleşen User nesnelerini döndürür.
    """
    if not text:
        return User.objects.none()
    usernames = MENTION_REGEX.findall(text)
    if not usernames:
        return User.objects.none()
    return User.objects.filter(username__in=usernames)


def render_mentions_html(text):
    """
    Metin içindeki @username kalıplarını tıklanabilir linklere dönüştürür.
    Sadece veritabanında var olan kullanıcılar için link oluşturur.
    """
    if not text:
        return text
    usernames = MENTION_REGEX.findall(text)
    if not usernames:
        return text
    existing = set(
        User.objects.filter(username__in=usernames).values_list('username', flat=True)
    )
    def replace_mention(match):
        username = match.group(1)
        if username in existing:
            return (
                f'<a href="/profile/{username}/" '
                f'class="mention-link" '
                f'title="@{username}">@{username}</a>'
            )
        return match.group(0)
    return MENTION_REGEX.sub(replace_mention, text)
