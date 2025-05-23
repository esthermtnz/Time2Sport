import django
import os
import random
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'time2sport.settings')
django.setup()

from sgu.models import User
from src.models import Session, Reservation
from sbai.models import SportFacility, Activity, Schedule, Photo, Bonus, DayOfWeek
from slegpn.models import Notification, ProductBonus

def get_images_from_folder(folder_path):
    ''' Get all image files from a given folder path '''
    if not os.path.exists(folder_path):
        return []
    return [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]


def create_schedule(day, hour_ranges):
    ''' Create schedules for a given day and hour ranges '''
    schedules = []
    for hour_begin, hour_end in hour_ranges:
        schedule = Schedule.objects.create(
            day_of_week=day,
            hour_begin=hour_begin,
            hour_end=hour_end
        )
        schedules.append(schedule)
    return schedules


def populate():
    ''' Populate the database '''

    # Activity schedules
    activity_schedules = {
        'Partido de Fútbol': {
            0: [('08:00:00', '09:00:00'), ('11:00:00', '12:00:00')],
            DayOfWeek.MARTES: [('09:00:00', '11:00:00')],
            DayOfWeek.VIERNES: [('08:00:00', '10:00:00')]
        },
        'Entrenamiento de Tenis': {
            DayOfWeek.LUNES: [('10:00:00', '12:00:00')],
            DayOfWeek.MIERCOLES: [('14:00:00', '16:00:00')],
            DayOfWeek.SABADO: [('09:00:00', '11:00:00')]
        },
        'Entrenamiento de Baloncesto': {
            DayOfWeek.JUEVES: [('17:00:00', '19:00:00')],
            DayOfWeek.DOMINGO: [('10:00:00', '12:00:00')]
        },
        'Clases de Natación': {
            DayOfWeek.LUNES: [('07:00:00', '08:00:00')],
            DayOfWeek.MIERCOLES: [('15:00:00', '16:00:00')],
            DayOfWeek.VIERNES: [('18:00:00', '19:30:00')]
        },
        'Entrenamiento de Carrera': {
            DayOfWeek.MARTES: [('06:00:00', '07:00:00'), ('19:00:00', '20:00:00')],
            DayOfWeek.JUEVES: [('08:00:00', '09:00:00')]
        }
    }

    # Facility schedules
    facility_schedules = {
        'Campo de Fútbol': {
            DayOfWeek.LUNES: [('07:00:00', '10:00:00')],
            DayOfWeek.MIERCOLES: [('12:00:00', '15:00:00')],
            DayOfWeek.SABADO: [('10:00:00', '12:00:00')]
        },
        'Pista de Tenis': {
            DayOfWeek.MARTES: [('08:00:00', '10:00:00')],
            DayOfWeek.JUEVES: [('16:00:00', '18:00:00')],
            DayOfWeek.DOMINGO: [('09:00:00', '11:00:00')]
        }
    }

    # Activities
    activities = [
        {'name': 'Partido de Fútbol', 'location': 'Campo de Fútbol',
            'description': 'Un partido de fútbol con equipos.', 'activity_type': 'Terrestre'},
        {'name': 'Entrenamiento de Tenis', 'location': 'Pista de Tenis',
            'description': 'Sesión de entrenamiento de tenis.', 'activity_type': 'Terrestre'},
        {'name': 'Entrenamiento de Baloncesto', 'location': 'Cancha de Baloncesto',
            'description': 'Entrenamiento de habilidades de baloncesto.', 'activity_type': 'Terrestre'},
        {'name': 'Clases de Natación', 'location': 'Piscina',
            'description': 'Clases de natación para todos los niveles.', 'activity_type': 'Acuática'},
        {'name': 'Entrenamiento de Carrera', 'location': 'Pista de Atletismo',
            'description': 'Sesión de entrenamiento cardiovascular.', 'activity_type': 'Terrestre'}
    ]

    # Facilities
    facilities = [
        {'name': 'Campo de Fútbol', 'number_of_facilities': 2,
            'description': 'Un gran campo de fútbol al aire libre.', 'hour_price': 50.0, 'facility_type': 'Exterior'},
        {'name': 'Pista de Tenis', 'number_of_facilities': 2,
            'description': 'Una pista de tenis bien mantenida.', 'hour_price': 30.0, 'facility_type': 'Exterior'}
    ]

    # Bonuses
    bonuses = [
        {'bonus_type': 'annual', 'price': 200.0},
        {'bonus_type': 'semester', 'price': 25.0},
        {'bonus_type': 'single', 'price': 5.0},
    ]

    # Create activities and assign schedules
    for act in activities:
        activity = Activity.objects.create(
            name=act['name'],
            location=act['location'],
            description=act['description'],
            activity_type=act['activity_type']
        )

        schedules = []
        for day, hours in activity_schedules.get(activity.name, {}).items():
            schedules.extend(create_schedule(day, hours))

        activity.schedules.set(schedules)

        # Associate existing images
        activity_images_folder = f'media/activities/{activity.id}'
        image_files = get_images_from_folder(activity_images_folder)

        for image_file in image_files:
            photo = Photo.objects.create(
                activity=activity, image=f"activities/{activity.id}/{image_file}")
            print(f'Added image {photo.image} to activity {activity.name}')

        for bon in bonuses:
            bonus = Bonus.objects.create(
                activity=activity,
                bonus_type=bon['bonus_type'],
                price=bon['price'],
            )
            print(bonus)

        sessions_act = Session.create_sessions(
            schedules, activity=activity, capacity=1)

    # Create facilities and assign schedules
    for fac in facilities:
        schedules = []
        for day, hours in facility_schedules.get(fac['name'], {}).items():
            schedules.extend(create_schedule(day, hours))

        facility = SportFacility.objects.create(
            name=fac['name'],
            number_of_facilities=fac['number_of_facilities'],
            description=fac['description'],
            hour_price=fac['hour_price'],
            facility_type=fac['facility_type'],
            schedules=schedules
        )

        # Associate existing images
        facility_images_folder = f'media/facilities/{facility.id}'
        image_files = get_images_from_folder(facility_images_folder)

        for image_file in image_files:
            photo = Photo.objects.create(
                facility=facility, image=f"facilities/{facility.id}/{image_file}")
            print(f'Added image {photo.image} to facility {facility.name}')

        sesions_fac = Session.create_sessions(schedules, facility=facility)

    print(sessions_act)
    print(sesions_fac)

    print("Population completed!")


if __name__ == '__main__':
    print("Starting application population script...")
    populate()
    print("Done!")
