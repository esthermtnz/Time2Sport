from django.shortcuts import render

# Create your views here.
def login(request):
    context = {}
    return render(request, 'gestion_deportiva/login.html', context)

from django.conf import settings
ms_identity_web = settings.MS_IDENTITY_WEB

@ms_identity_web.login_required
def secret_page(request):
    return render(request, 'secret.html', {})