from django import template

register = template.Library()


@register.simple_tag
def get_dashboard_stats():
    """Admin dashboard istatistiklerini template context'e yükler."""
    from forum.services.dashboard_service import get_dashboard_context
    return get_dashboard_context()
