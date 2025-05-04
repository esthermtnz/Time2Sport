from django.shortcuts import render


class Custom404:
    ''' Middleware to handle 404 errors and render to a custom 404 template '''

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if response.status_code == 404:
            return render(request, '404.html', status=404)
        return response
