from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.shortcuts import redirect
from django.contrib.auth.models import User
from datetime import timedelta

@receiver(user_logged_in)
def first_login_redirect(sender, request, user, **kwargs):
    print(f"⚡ Señal activada: {user.username} ha iniciado sesión")  
    print(f"Fecha de registro: {user.date_joined} | Último login: {user.last_login}")

    if user.is_authenticated and abs((user.date_joined - user.last_login).total_seconds()) < 5:
        print("✅ Primera vez que inicia sesión, activando redirección...")
        request.session['first_login'] = True  
    else:
        print("❌ No es la primera vez que inicia sesión")