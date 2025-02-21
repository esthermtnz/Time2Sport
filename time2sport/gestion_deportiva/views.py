import os
import json

from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth import login, logout

__version__ = "0.5.0"

User = get_user_model()  

# Create your views here.
def log_in(request):
    context = {}
    return render(request, 'gestion_deportiva/log_in.html', context)

@settings.AUTH.login_required
def log_out(request, *, context):
    logout(request)
    return redirect('http://localhost:8000/')  


@settings.AUTH.login_required
def index(request, *, context):
    user_info = context['user']  # Información del usuario autenticado en Microsoft

    # Extraer datos del usuario desde el contexto de Microsoft
    email = user_info.get("preferred_username")  # Microsoft devuelve el email aquí
    full_name = user_info.get("name", "")  # Nombre completo
    name_parts = full_name.split()

    first_name = name_parts[0] if name_parts else ""
    last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""

    print(f"email: {email}, first_name: {first_name}, last_name: {last_name}")

    # Buscar si el usuario ya existe
    user, created = User.objects.get_or_create(
        email=email,
        defaults={
            "username": email,  # Puedes cambiarlo si prefieres otro identificador
            "first_name": first_name,
            "last_name": last_name,
        }
    )

    if created:
        print(f"Nuevo usuario creado: {email}")

    # Iniciar sesión automáticamente al usuario en Django
    login(request, user)

    return render(request, 'gestion_deportiva/home.html', {"user": user})

@settings.AUTH.login_required
def profile(request, *, context):
    context = {}
    return render(request, 'gestion_deportiva/profile.html', context)