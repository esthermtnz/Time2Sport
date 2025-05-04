from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

import random
import string
import time

import os
import json

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth import login, logout
from django.contrib import messages
from django.core.files.storage import default_storage
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from django.utils.timezone import now

from .forms import ContactForm, UAMForm
from django.core.mail import EmailMessage


__version__ = "0.5.0"

User = get_user_model()


# -- Login and Logout

def log_in(request):
    """Load the login template"""
    context = {}
    return render(request, 'users/log_in.html', context)


@login_required
def log_out(request):
    """Logsout the user and redircets to login page"""
    logout(request)
    return redirect('http://localhost:8000/')

# -- Footer Views


def aviso_legal(request):
    """Load the Aviso Legal template"""
    context = {}
    return render(request, 'footer/aviso_legal.html', context)


def politica_privacidad(request):
    """Load the privacy polacy template"""
    context = {}
    return render(request, 'footer/politica_privacidad.html', context)


def contacto(request):
    """Allow the user to send an email to the admin"""
    contactForm = ContactForm()

    if request.method == "POST":
        contactForm = ContactForm(data=request.POST)

        if contactForm.is_valid():
            asunto = request.POST.get("asunto")
            nombre = request.POST.get("nombre")
            email = request.POST.get("email")
            contenido = request.POST.get("contenido")

            mensaje_html = f"""
                <html>
                    <body>
                        <p>Hola,</p>
                        <p>Has recibido un nuevo mensaje a través del formulario de contacto.</p>
                        <p><strong>📌 Asunto:</strong> {asunto}</p>
                        <p><strong>👤 Nombre:</strong> {nombre}</p>
                        <p><strong>📧 Correo electrónico:</strong> {email}</p>
                        <hr>
                        <p><strong>📝 Mensaje:</strong></p>
                        <p>{contenido}</p>
                        <hr>
                        <p>Este mensaje ha sido enviado desde el formulario de contacto de Time2Sport.</p>
                    </body>
                </html>
            """

            emailMessage = EmailMessage(asunto, mensaje_html, "", [
                                        "time2sportuam@gmail.com"], reply_to=[email])
            emailMessage.content_subtype = "html"

            try:
                emailMessage.send()
                return redirect("/contacto/?valido")
            except:
                return redirect("/contacto/?invalido")

    return render(request, 'footer/contacto.html', {"contactForm": contactForm})


# -- Home page

@login_required
def uam_verification(request):
    """Allow the user to select user type and sends a code to the email in case of UAM"""
    form = UAMForm()

    # If user is already from UAM, redirect to home
    if request.user.is_uam:
        return redirect('index')

    if request.method == "POST":
        form = UAMForm(data=request.POST)

        if form.is_valid():
            user_choice = request.POST.get("user_choice")
            email = request.POST.get("email_uam")
            usuario = request.user

            user_type_map = {
                "1": "notUAM",
                "2": "student",
                "3": "professor",
                "4": "administrative",
                "5": "alumni",
            }
            usuario.user_type = user_type_map.get(user_choice)

            if usuario.user_type == "notUAM":
                usuario.is_uam = False
                usuario.save()
                return redirect('index')
            else:
                # usuario.save()

                codigo = ''.join(random.choices(
                    string.ascii_uppercase + string.digits, k=6))
                expiration_time = now() + timedelta(minutes=10)

                request.session["codigo_verificacion"] = codigo
                request.session["email_verificacion"] = email
                request.session["codigo_expiracion"] = expiration_time.timestamp()
                request.session["user_type"] = usuario.user_type

                mensaje = f"""
                    Hola,

                    Por favor, introduce el siguiente código en la aplicación para verificar tu cuenta UAM:

                    {codigo}

                    Este código es de un solo uso. El código expirará en 10 minutos.
                """

                emailMessage = EmailMessage(
                    subject="Verificación Credenciales UAM - Time2Sport",
                    body=mensaje,
                    from_email="time2sportuam@gmail.com",
                    to=[email],
                )

                try:
                    emailMessage.send()
                    return redirect("/verificar-codigo-uam/")
                except:
                    return redirect("/uam-verification/?invalido")

    return render(request, 'users/uam_verification.html', {"form": form})


@login_required
def verificar_codigo_uam(request):
    """Verifies that the code sent is the same as the introduced and sets the user as UAM successfully"""
    # If user is already from UAM, redirect to home
    if request.user.is_uam:
        return redirect('index')

    if request.method == "POST":
        codigo_form = request.POST.get("codigo")

        codigo_correcto = request.session.get("codigo_verificacion")
        tiempo_expiracion = request.session.get("codigo_expiracion")
        email = request.session.get("email_verificacion")
        user_type = request.session.get("user_type")

        if not codigo_correcto or not tiempo_expiracion:
            return redirect("/uam-verification/?expirado")

        if now().timestamp() > tiempo_expiracion:
            del request.session["codigo_verificacion"]
            del request.session["codigo_expiracion"]
            del request.session["email_verificacion"]
            return redirect("/uam-verification/?expirado")

        if codigo_form == codigo_correcto:
            usuario = request.user
            usuario.is_uam = True
            usuario.user_type = user_type
            usuario.save()

            del request.session["codigo_verificacion"]
            del request.session["codigo_expiracion"]
            del request.session["email_verificacion"]

            return redirect("/home")
        else:
            return render(request, "users/verificar_codigo_uam.html", {"error": "Código incorrecto"})

    return render(request, "users/verificar_codigo_uam.html")


@login_required
def index(request):
    """Loads the home page and calls calls UAM verification if it's the first login"""
    if request.session.pop('first_login', False):
        return redirect('uam_verification')

    return render(request, 'home.html')


# Edit profile
@login_required
def profile(request):
    """Loads the profile template and the user data"""
    user_types = {
        "notUAM": "No pertenece a la UAM",
        "student": "Estudiante UAM",
        "professor": "Profesional docente o investigador UAM",
        "administrative": "Profesional administrativo UAM",
        "alumni": "Antiguo Alumno de la UAM",
    }
    user_type = user_types.get(request.user.user_type, "Desconocido")

    context = {"user": request.user, "user_type": user_type}
    return render(request, 'users/profile.html', context)


@login_required
def edit_profile(request):
    """Edit the user profile picture"""
    if request.method == 'POST' and request.FILES.get('profile_image'):
        request.user.editProfile(request.FILES['profile_image'])
    return redirect('profile')
