class DisableHostCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.META['HTTP_HOST'] = 'localhost:8006'
        return self.get_response(request)
