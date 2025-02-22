from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from .models import Activity, SportFacility

def all_activities(request):
    activities = Activity.objects.prefetch_related('photos').all()
    return render(request, 'activities/all_activities.html', {'activities': activities})

def activity_detail(request, activity_id):
    activity = get_object_or_404(Activity, pk=activity_id)
    return render(request, 'activities/activity_detail.html', {'activity': activity})

def all_facilities(request):
    facilities = SportFacility.objects.prefetch_related('photos').all()
    return render(request, 'facilities/all_facilities.html', {'facilities': facilities})

def facility_detail(request, facility_id):
    facility = get_object_or_404(SportFacility, pk=facility_id)
    return render(request, 'facilities/facility_detail.html', {'facility': facility})

def home(request):
    return render(request, 'home.html')

def schedules(request):
    return render(request, 'schedules/schedules.html')

def facilities_schedule(request):
    facilities = SportFacility.objects.prefetch_related('schedules').all()
    return render(request, 'schedules/facilities_schedule.html', {'facilities': facilities})

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

    return render(request, "schedules/activities_schedule.html", {"activities": grouped_schedules})

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

    return render(request, 'search_results.html', {
        'facilities': facilities,
        'activities': activities,
        'query': query,
        'category': category
    })
