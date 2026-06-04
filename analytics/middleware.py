_SKIP_PREFIXES = (
    '/static/', '/media/', '/admin/', '/api/', '/ws/',
    '/favicon', '/accounts/', '/login/', '/logout/',
    '/sitemap', '/robots', '/.well-known/', '/534e',
)


class PageViewMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if (
            request.method == 'GET'
            and getattr(request, 'user', None) is not None
            and request.user.is_authenticated
            and response.status_code == 200
            and not any(request.path.startswith(p) for p in _SKIP_PREFIXES)
        ):
            try:
                from analytics.models import PageView
                from analytics.utils import resolve_tab_name
                PageView.objects.create(
                    user=request.user,
                    path=request.path[:200],
                    tab_name=resolve_tab_name(request.path),
                )
            except Exception:
                pass
        return response
