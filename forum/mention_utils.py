import re
from django.contrib.auth.models import User

MENTION_REGEX = re.compile(r'@(\w+)')
URL_REGEX = re.compile(r'(https?://[^\s<>"]+)')


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
    Metin içindeki @username kalıplarını ve URL'leri tıklanabilir linklere dönüştürür.
    """
    if not text:
        return text

    # @mentions
    usernames = MENTION_REGEX.findall(text)
    if usernames:
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
        text = MENTION_REGEX.sub(replace_mention, text)

    # URL'leri tıklanabilir yap (zaten <a> içinde olmayanlar)
    text = URL_REGEX.sub(
        r'<a href="\1" target="_blank" rel="noopener noreferrer" class="text-info">\1</a>',
        text
    )

    # Satır sonlarını <br> yap
    text = text.replace('\n', '<br>')

    return text
