# Bypass Django's RFC hostname validation so Docker service names with
# underscores (e.g. "ai_service") are accepted as valid HTTP_HOST values.
import django.http.request as _django_request
_django_request.validate_host = lambda host, allowed_hosts: True


class AllowDockerHostMiddleware:
    """No-op middleware — the module-level patch above does the real work."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)
