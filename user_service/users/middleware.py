class DisableHostCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Completely bypass host validation by setting a valid host
        request.META['HTTP_HOST'] = 'localhost:8004'
        response = self.get_response(request)
        return response