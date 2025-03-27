from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from .models import Activity, SportFacility

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


#-- Login and Logout

def log_in(request):
    context = {}
    return render(request, 'gestion_deportiva/users/log_in.html', context)


@login_required
def log_out(request):
    logout(request)
    return redirect('http://localhost:8000/')  

#-- Footer Views
def aviso_legal(request):
    context = {}
    return render(request, 'gestion_deportiva/footer/aviso_legal.html', context)

def politica_privacidad(request):
    context = {}
    return render(request, 'gestion_deportiva/footer/politica_privacidad.html', context)

def contacto(request):
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

            emailMessage = EmailMessage(asunto, mensaje_html, "", ["time2sportuam@gmail.com"], reply_to=[email])
            emailMessage.content_subtype = "html"

            try:
                emailMessage.send()
                return redirect("/contacto/?valido")
            except:
                return redirect("/contacto/?invalido")

    return render(request, 'gestion_deportiva/footer/contacto.html', {"contactForm": contactForm})


#-- Home page

@login_required
def uam_verification(request):
    form = UAMForm()

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
                usuario.save()

                codigo = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
                expiration_time = now() + timedelta(minutes=10)

                request.session["codigo_verificacion"] = codigo
                request.session["email_verificacion"] = email
                request.session["codigo_expiracion"] = expiration_time.timestamp()

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


    return render(request, 'gestion_deportiva/users/uam_verification.html', {"form": form})

@login_required
def verificar_codigo_uam(request):
    if request.method == "POST":
        codigo_form = request.POST.get("codigo")

        codigo_correcto = request.session.get("codigo_verificacion")
        tiempo_expiracion = request.session.get("codigo_expiracion")
        email = request.session.get("email_verificacion")

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
            usuario.save()

            del request.session["codigo_verificacion"]
            del request.session["codigo_expiracion"]
            del request.session["email_verificacion"]

            return redirect("/home")
        else:
            return render(request, "gestion_deportiva/users/verificar_codigo_uam.html", {"error": "Código incorrecto"})

    return render(request, "gestion_deportiva/users/verificar_codigo_uam.html")

@login_required
def index(request):
    if request.session.pop('first_login', False): 
        return redirect('uam_verification') 
    
    return render(request, 'gestion_deportiva/home.html')


#Edit profile
@login_required
def profile(request):

    user_types = {
        "notUAM": "No pertenece a la UAM",
        "student": "Estudiante UAM",
        "professor": "Profesional docente o investigador UAM",
        "administrative": "Profesional administrativo UAM",
        "alumni": "Antiguo Alumno de la UAM",
    }
    user_type = user_types.get(request.user.user_type, "Desconocido")
    
    context = {"user": request.user, "user_type": user_type}
    return render(request, 'gestion_deportiva/users/profile.html', context)



@login_required
def edit_profile(request):
    if request.method == 'POST' and request.FILES.get('profile_image'):
        request.user.editProfile(request.FILES['profile_image'])
    return redirect('profile') 

# -- SBAI

@login_required
def all_activities(request):
    activities = Activity.objects.prefetch_related('photos').all()
    return render(request, 'gestion_deportiva/activities/all_activities.html', {'activities': activities})

@login_required
def activity_detail(request, activity_id):
    activity = get_object_or_404(Activity, pk=activity_id)
    return render(request, 'gestion_deportiva/activities/activity_detail.html', {'activity': activity})

@login_required
def all_facilities(request):
    facilities = SportFacility.objects.prefetch_related('photos').all()
    return render(request, 'gestion_deportiva/facilities/all_facilities.html', {'facilities': facilities})

@login_required
def facility_detail(request, facility_id):
    facility = get_object_or_404(SportFacility, pk=facility_id)
    return render(request, 'gestion_deportiva/facilities/facility_detail.html', {'facility': facility})

@login_required
def schedules(request):
    return render(request, 'gestion_deportiva/schedules/schedules.html')

@login_required
def facilities_schedule(request):
    facilities = SportFacility.objects.prefetch_related('schedules').all()
    return render(request, 'gestion_deportiva/schedules/facilities_schedule.html', {'facilities': facilities})

@login_required
def download_facilities_schedule(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="facilities_schedule.pdf"'

    # Crear el documento
    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # Título del documento
    elements.append(Paragraph("Horarios de Instalaciones", styles["Title"]))
    elements.append(Spacer(1, 12))

    # Columnas de la tabla
    data = [["Instalación", "Horario"]]

    facilities = SportFacility.objects.prefetch_related('schedules').all()

    # Recopilar los horarios de las instalaciones
    for facility in facilities:
        horarios = "\n".join(
            [f"{schedule.day_of_week}: {schedule.hour_begin} - {schedule.hour_end}" for schedule in facility.schedules.all()]
        )
        data.append([facility.name, horarios])

    # Crear la tabla
    table = Table(data, colWidths=[200, 250])  # Ajuste de ancho de columnas
    # Poner estilos a la tabla
    table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
    ]))

    # Añadir la tabla al documento
    elements.append(table)
    doc.build(elements)
    # Devolver el PDF
    return response

@login_required
def activities_schedule(request):
    activities = Activity.objects.all()

    # If there are activities with several schedules, group them
    grouped_schedules = []
    for activity in activities:
        schedule_dict = {}

        for schedule in activity.schedules.all():
            day = schedule.day_of_week
            time_range = f"{schedule.hour_begin.strftime('%H:%M')} - {schedule.hour_end.strftime('%H:%M')}"

            if day not in schedule_dict:
                schedule_dict[day] = []

            # Update the list of schedules for the day
            schedule_dict[day].append(time_range)

        # Save the schedules formatted for the template
        formatted_schedules = [
            {"day": day, "times": "\n".join(times)}
            for day, times in schedule_dict.items()
        ]

        # Save the activity with its schedules
        grouped_schedules.append({
            "name": activity.name,
            "schedules": formatted_schedules
        })

    return render(request, "gestion_deportiva/schedules/activities_schedule.html", {"activities": grouped_schedules})

@login_required
def download_activities_schedule(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="activities_schedule.pdf"'

    # Crear el documento
    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # Título del documento
    elements.append(Paragraph("Horarios de Actividades", styles["Title"]))
    elements.append(Spacer(1, 12))

    # Encabezados de la tabla
    data = [["Actividad", "Día", "Horario"]]
    merge_styles = [] # Aquí se guardan las actividades con varios horarios para luego combinar las celdas

    activities = Activity.objects.prefetch_related('schedules').all()

    for activity in activities:
        schedules_by_day = {}

        # Agrupar horarios por día
        for schedule in activity.schedules.all():
            if schedule.day_of_week not in schedules_by_day:
                schedules_by_day[schedule.day_of_week] = []
            schedules_by_day[schedule.day_of_week].append(f"{schedule.hour_begin.strftime('%I:%M')} - {schedule.hour_end.strftime('%I:%M')}")

        activity_rows = [] # Filas de la misma actividad
        for day, hours in schedules_by_day.items():
            grouped_hours = "\n".join(hours)
            activity_rows.append(["", day, grouped_hours])

        if activity_rows:
            # Poner el nombre de la actividad en la primera fila del grupo
            activity_rows[0][0] = activity.name
            data.extend(activity_rows)

            # Agrupar las celdas de la columna de la actividad si hay más de una fila
            if len(activity_rows) > 1:
                merge_styles.append(('SPAN', (0, len(data) - len(activity_rows)), (0, len(data) - 1)))

    # Poner estilos a la tabla
    table = Table(data, colWidths=[150, 100, 150])
    table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ] + merge_styles))

    # Añadir la tabla al documento
    elements.append(table)
    # Crear el PDF
    doc.build(elements)
    return response

from django.db.models import Q

@login_required
def search_results(request):
    facilities = SportFacility.objects.all()
    activities = Activity.objects.all()
    category = None
    query = None

    if request.method == "POST":
        category = request.POST.get('category', '').strip()
        query = request.POST.get('q', '').strip()

        if query:
            facilities = facilities.filter(
                Q(name__icontains=query)
            )
            activities = activities.filter(
                Q(name__icontains=query)
            )

        if category:
            category = category.capitalize()
            if category in ['Interior', 'Exterior']:
                facilities = facilities.filter(facility_type=category)
                activities = None
            elif category in ['Terrestre', 'Acuática']:
                activities = activities.filter(activity_type=category)
                facilities = None

    return render(request, 'gestion_deportiva/search_results.html', {
        'facilities': facilities,
        'activities': activities,
        'query': query,
        'category': category
    })

