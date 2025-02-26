from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from .models import Activity, SportFacility

import os
import json

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth import login, logout
from django.contrib import messages
from django.core.files.storage import default_storage

__version__ = "0.5.0"

User = get_user_model()

def all_activities(request):
    activities = Activity.objects.prefetch_related('photos').all()
    return render(request, 'gestion_deportiva/activities/all_activities.html', {'activities': activities})

def activity_detail(request, activity_id):
    activity = get_object_or_404(Activity, pk=activity_id)
    return render(request, 'gestion_deportiva/activities/activity_detail.html', {'activity': activity})

def all_facilities(request):
    facilities = SportFacility.objects.prefetch_related('photos').all()
    return render(request, 'gestion_deportiva/facilities/all_facilities.html', {'facilities': facilities})

def facility_detail(request, facility_id):
    facility = get_object_or_404(SportFacility, pk=facility_id)
    return render(request, 'gestion_deportiva/facilities/facility_detail.html', {'facility': facility})

def schedules(request):
    return render(request, 'gestion_deportiva/schedules/schedules.html')

def facilities_schedule(request):
    facilities = SportFacility.objects.prefetch_related('schedules').all()
    return render(request, 'gestion_deportiva/schedules/facilities_schedule.html', {'facilities': facilities})

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

def politica_privacidad(request):
    context = {}
    return render(request, 'gestion_deportiva/politica_privacidad.html', context)

def contacto(request):
    context = {}
    return render(request, 'gestion_deportiva/contacto.html', context)


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
