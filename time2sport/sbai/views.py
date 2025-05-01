from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from .models import Activity, SportFacility, DayOfWeek, Schedule

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
from django.utils import timezone

from django.core.mail import EmailMessage
from django.db.models import Q

from src.models import Session

@login_required
def all_activities(request):
    activities = Activity.objects.prefetch_related('photos').all()
    return render(request, 'activities/all_activities.html', {'activities': activities})

@login_required
def activity_detail(request, activity_id):
    activity = get_object_or_404(Activity, pk=activity_id)

    has_bono = request.user.has_valid_bono_for_activity(activity)

    if not has_bono:
        return render(request, 'activities/activity_detail.html', {
            'activity': activity,
            'has_bono': has_bono,
            'bonuses': activity.bonuses.all()
        })

    sessions = Session.objects.filter(activity_id=activity_id)

    ordered_sessions = sessions.order_by("date", "schedule__hour_begin")

    # Get the first user in the waiting list of each session, if any
    # To show only the reservation button to the first one if the session is not full due to a cancellation
    for session in ordered_sessions:
        waiting_list = session.waiting_list.all()
        if waiting_list.exists():
            is_first_user = waiting_list.first()
            if is_first_user.user == request.user:
                if not session.is_full():
                    session.is_first_user = True
                else:
                    session.is_first_user = False
            else:
                session.is_first_user = False
        else:
            session.is_first_user = True

    return render(request, 'activities/activity_detail.html', {
        'activity': activity,
        'has_bono': has_bono,
        'sessions': ordered_sessions
    })

@login_required
def all_facilities(request):
    all_facilities = SportFacility.objects.prefetch_related('photos')
    facilities = []
    # If a facility has more than one instance, show only one
    for f in all_facilities:
        if f.number_of_facilities > 1:
            # Get the first instance
            if not f.name.split(" ")[-1].isdigit():
                name = f.name
                facilities.append(f)
        else:
            facilities.append(f)

    return render(request, 'facilities/all_facilities.html', {'facilities': facilities})


def divide_hours_into_blocks(schedule):
    blocks = []
    start = schedule.hour_begin
    end = schedule.hour_end
    while start < end:
        siguiente = (datetime.combine(datetime.today(), start) + timedelta(hours=1)).time()
        blocks.append({'start': start, 'end': siguiente})
        start = siguiente
    return blocks


@login_required
def facility_detail(request, facility_id):
    # Get the facility by id
    facility = get_object_or_404(SportFacility, pk=facility_id)

    # Check if the facility has multiple instances
    if facility.number_of_facilities == 1:
        facilities = [facility]
        name = facility.name
    else:
        if facility.name.split(" ")[-1].isdigit():
            name = ' '.join(facility.name.split(" ")[:-1])
        else:
            name = facility.name
        facilities = SportFacility.objects.filter(name__regex=f"^{name}( [0-9]+)?$").prefetch_related('photos')

    # Get the next 7 days
    today = timezone.now().date()
    next_7_days = [today + timedelta(days=i) for i in range(7)]

    # Get the schedules for the next 7 days
    sessions_next_7_days = []
    for day in next_7_days:
        day_of_week = day.weekday() # Get the day of the week (0 is Monday ... 6 is Sunday)

        # Sessions for each facility on the current day
        all_sessions_of_the_day = []

        for f in facilities:
            # Get the daily schedules matching the day of the week for this facility
            session_of_the_day = f.sessions.filter(date=day)
            all_sessions_of_the_day.append({
                'facility': f,
                'sessions': session_of_the_day
            })

        sessions_next_7_days.append({
            'date': day,
            'sessions': all_sessions_of_the_day
        })

    return render(request, 'facilities/facility_detail.html', {
        'facility': facility,
        'name': name,
        'next_7_days': next_7_days,
        'sessions_next_7_days': sessions_next_7_days
    })

@login_required
def schedules(request):
    return render(request, 'schedules/schedules.html')

@login_required
def facilities_schedule(request):
    facilities = SportFacility.objects.prefetch_related('schedules').all()
    return render(request, 'schedules/facilities_schedule.html', {'facilities': facilities})

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
            [f"{schedule.get_day_of_week_display()}: {schedule.hour_begin} - {schedule.hour_end}" for schedule in facility.schedules.all()]
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
            day = schedule.get_day_of_week_display()
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

    return render(request, "schedules/activities_schedule.html", {"activities": grouped_schedules})

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
            day = schedule.get_day_of_week_display()
            if day not in schedules_by_day:
                schedules_by_day[day] = []
            schedules_by_day[day].append(f"{schedule.hour_begin.strftime('%I:%M')} - {schedule.hour_end.strftime('%I:%M')}")

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

    return render(request, 'search_results.html', {
        'facilities': facilities,
        'activities': activities,
        'query': query,
        'category': category
    })
