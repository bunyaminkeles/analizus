from django import template

register = template.Library()


@register.simple_tag
def get_dashboard_stats():
    """Admin dashboard istatistiklerini template context'e yükler."""
    from forum.services.dashboard_service import get_dashboard_context
    return get_dashboard_context()


@register.simple_tag
def get_queue_status():
    """Tüm job modellerindeki running/pending işleri döndürür."""
    try:
        from tezanaliz.models import TezAnaliz
        from makaleanaliz.models import MakaleAnaliz
        from yoktez.models import YokTezSearchJob
        from openalex.models import AlexSearchJob
        from trdizin.models import DizinSearchJob
        from bibliometrics.models import BibliometricJob
        from django.utils import timezone

        sections = [
            ('Tez Analizi', TezAnaliz, 'tezanaliz'),
            ('Makale Analizi', MakaleAnaliz, 'makaleanaliz'),
            ('YÖK Tez', YokTezSearchJob, 'yoktez'),
            ('OpenAlex', AlexSearchJob, 'openalex'),
            ('TR Dizin', DizinSearchJob, 'trdizin'),
            ('Bibliometrik', BibliometricJob, 'bibliometrics'),
        ]

        rows = []
        for label, Model, job_type in sections:
            for job in Model.objects.filter(status='running').select_related('user').order_by('created_at'):
                rows.append({
                    'type': label,
                    'status': 'running',
                    'status_label': 'Çalışıyor',
                    'user': job.user.username if job.user_id else '-',
                    'created_at': job.created_at,
                    'id_short': str(job.id)[:8],
                })
            for job in Model.objects.filter(status='pending').select_related('user').order_by('created_at'):
                rows.append({
                    'type': label,
                    'status': 'pending',
                    'status_label': 'Bekliyor',
                    'user': job.user.username if job.user_id else '-',
                    'created_at': job.created_at,
                    'id_short': str(job.id)[:8],
                })

        return {
            'rows': rows,
            'total': len(rows),
            'running_count': sum(1 for r in rows if r['status'] == 'running'),
            'pending_count': sum(1 for r in rows if r['status'] == 'pending'),
        }
    except Exception:
        return {'rows': [], 'total': 0, 'running_count': 0, 'pending_count': 0}
