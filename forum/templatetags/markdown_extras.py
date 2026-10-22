import bleach
from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
import markdown as md

register = template.Library()

ALLOWED_TAGS = [
    'p', 'br', 'hr', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'strong', 'em', 'b', 'i', 'u', 'del',
    'ul', 'ol', 'li', 'dl', 'dt', 'dd',
    'blockquote', 'pre', 'code', 'span', 'div',
    'table', 'thead', 'tbody', 'tr', 'th', 'td',
    'a', 'img',
]

ALLOWED_ATTRIBUTES = {
    '*': ['class', 'id'],
    'a': ['href', 'title'],
    'img': ['src', 'alt', 'title'],
}

ALLOWED_PROTOCOLS = ['http', 'https', 'mailto']

@register.filter()
@stringfilter
def markdown(value):
    extensions = [
        'markdown.extensions.fenced_code',
        'markdown.extensions.codehilite',
        'markdown.extensions.tables',
        'markdown.extensions.nl2br',
        'markdown.extensions.toc',
    ]
    raw_html = md.markdown(value, extensions=extensions)
    clean_html = bleach.clean(
        raw_html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        protocols=ALLOWED_PROTOCOLS,
        strip=True,
    )
    return mark_safe(clean_html)