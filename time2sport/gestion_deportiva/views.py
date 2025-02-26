import os
import json

from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth import login, logout
from django.contrib import messages
from django.core.files.storage import default_storage

__version__ = "0.5.0"

User = get_user_model()  


def log_in(request):
    context = {}
    return render(request, 'gestion_deportiva/log_in.html', context)

@settings.AUTH.login_required
def log_out(request, *, context):
    logout(request)
    return redirect('http://localhost:8000/')  

# Footer Views
def aviso_legal(request):
    context = {}
    return render(request, 'gestion_deportiva/aviso_legal.html', context)


@settings.AUTH.login_required
def index(request, *, context):
    user_info = context['user']  

    # User's information
    email = user_info.get("preferred_username")  

    #Parse full name into first_name and last_name
    full_name = user_info.get("name", "")  
    name_parts = full_name.split()

    first_name = name_parts[0] if name_parts else ""
    last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""

    print(f"email: {email}, first_name: {first_name}, last_name: {last_name}")

    # Checks if the user exists and creates it
    user, created = User.objects.get_or_create(
        email=email,
        defaults={
            "username": email, 
            "first_name": first_name,
            "last_name": last_name,
        }
    )

    #Log in the user 
    login(request, user)

    return render(request, 'gestion_deportiva/home.html', {"user": user})

@settings.AUTH.login_required
def profile(request, *, context):
    context = {"user": request.user}
    return render(request, 'gestion_deportiva/profile.html', context)


@settings.AUTH.login_required
def edit_profile(request, *, context):
    if request.method == 'POST' and request.FILES.get('profile_image'):
        request.user.editProfile(request.FILES['profile_image'])
    return redirect('profile') 
