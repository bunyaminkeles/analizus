import re

from django import template
from django.utils.html import escape, urlize as django_urlize
from django.utils.safestring import mark_safe

register = template.Library()

MD_LINK_RE = re.compile(r'\[([^\[\]]+)\]\(\s*(https?://[^\s()]+)\s*\)')


@register.filter(is_safe=True)
def broadcast_body(value):
    """Admin toplu e-posta gövdesini HTML'e çevirir.

    - `[isim](https://...)` sözdizimini tıklanabilir linke çevirir
    - Geri kalan çıplak http(s) linklerini otomatik linkler
    - Boş satırla ayrılmış bloklar paragraf, tek satır sonları <br> olur
    - Tüm metin kaçışlıdır (admin girdisi işlenmeden önce escape edilir)
    """
    value = value or ''

    parts = MD_LINK_RE.split(value)
    rendered = []
    i = 0
    while i < len(parts):
        plain = parts[i]
        if plain:
            rendered.append(django_urlize(plain, nofollow=True, autoescape=True))
        if i + 2 < len(parts):
            link_text, link_url = parts[i + 1], parts[i + 2]
            rendered.append(f'<a href="{escape(link_url)}" rel="nofollow">{escape(link_text)}</a>')
        i += 3

    html = ''.join(rendered)

    paragraphs = re.split(r'\n\s*\n', html.strip())
    html = ''.join(
        f'<p>{p.replace(chr(10), "<br>")}</p>'
        for p in paragraphs if p.strip()
    )

    return mark_safe(html)
