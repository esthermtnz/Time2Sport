import django
import os
import random
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'time2sport.settings')
django.setup()

from sbai.models import SportFacility, Activity, Schedule, Photo, Bonus
from src.models import Session, Reservation
from django.contrib.auth.models import User

def get_images_from_folder(folder_path):
    if not os.path.exists(folder_path):
        return []
    return [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

def create_schedule(day, hour_ranges):
    schedules = []
    for hour_begin, hour_end in hour_ranges:
        schedule = Schedule.objects.create(
            day_of_week=day,
            hour_begin=hour_begin,
            hour_end=hour_end
        )
        schedules.append(schedule)
    return schedules





def create_sessions(schedules, activity=None, facility=None):
    if (activity and facility) or (not activity and not facility):
        return []

    sessions = []
    today = datetime.today()

    for schedule in schedules:

        day_of_week = schedule.day_of_week
        days_of_week = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        target_day_index = days_of_week.index(day_of_week)
        today_day_index = today.weekday() # 0 for Monday, 6 for Sunday

        days_diff = target_day_index - today_day_index
        if days_diff <= 0:
            days_diff += 7 # If the day has already passed, we need to add 7 days

        # Calculate the date of the first session
        first_session_date = today + timedelta(days=days_diff)

        for i in range(4): # Create sessions for the following month (4 weeks)
            session_date = first_session_date + timedelta(weeks=i)

            # Check if a session already exists for this schedule
            existing_session = Session.objects.filter(schedule=schedule, 
                                                      activity=activity if activity else None, 
                                                      facility=facility if facility else None).first()

            if not existing_session:
                session = Session.objects.create(
                    activity=activity if activity else None,
                    facility=facility if facility else None,
                    schedule=schedule,
                    date=session_date,
                    capacity=10,
                    free_places=10,
                )
                sessions.append(session)
            else:
                print(f"Session already exists for {activity.name if activity else facility.name} with schedule {schedule.id}")
                
    return sessions




def populate():
    activity_schedules = {
        'Partido de Fútbol': {
            'Lunes': [('08:00:00', '09:00:00'), ('11:00:00', '12:00:00')],
            'Martes': [('09:00:00', '11:00:00')],
            'Viernes': [('08:00:00', '10:00:00')]
        },
        'Entrenamiento de Tenis': {
            'Lunes': [('10:00:00', '12:00:00')],
            'Miércoles': [('14:00:00', '16:00:00')],
            'Sábado': [('09:00:00', '11:00:00')]
        },
        'Entrenamiento de Baloncesto': {
            'Jueves': [('17:00:00', '19:00:00')],
            'Domingo': [('10:00:00', '12:00:00')]
        },
        'Clases de Natación': {
            'Lunes': [('07:00:00', '08:00:00')],
            'Miércoles': [('15:00:00', '16:00:00')],
            'Viernes': [('18:00:00', '19:30:00')]
        },
        'Entrenamiento de Carrera': {
            'Martes': [('06:00:00', '07:00:00'), ('19:00:00', '20:00:00')],
            'Jueves': [('08:00:00', '09:00:00')]
        }
    }

    facility_schedules = {
        'Campo de Fútbol': {
            'Lunes': [('07:00:00', '10:00:00')],
            'Miércoles': [('12:00:00', '15:00:00')],
            'Sábado': [('10:00:00', '12:00:00')]
        },
        'Pista de Tenis': {
            'Martes': [('08:00:00', '10:00:00')],
            'Jueves': [('16:00:00', '18:00:00')],
            'Domingo': [('09:00:00', '11:00:00')]
        }
    }

    activities = [
        {'name': 'Partido de Fútbol', 'location': 'Campo de Fútbol', 'description': 'Un partido de fútbol con equipos.', 'activity_type': 'Terrestre'},
        {'name': 'Entrenamiento de Tenis', 'location': 'Pista de Tenis', 'description': 'Sesión de entrenamiento de tenis.', 'activity_type': 'Terrestre'},
        {'name': 'Entrenamiento de Baloncesto', 'location': 'Cancha de Baloncesto', 'description': 'Entrenamiento de habilidades de baloncesto.', 'activity_type': 'Terrestre'},
        {'name': 'Clases de Natación', 'location': 'Piscina', 'description': 'Clases de natación para todos los niveles.', 'activity_type': 'Acuática'},
        {'name': 'Entrenamiento de Carrera', 'location': 'Pista de Atletismo', 'description': 'Sesión de entrenamiento cardiovascular.', 'activity_type': 'Terrestre'}
    ]

    facilities = [
        {'name': 'Campo de Fútbol', 'number_of_facilities': 2, 'description': 'Un gran campo de fútbol al aire libre.', 'hour_price': 50.0, 'facility_type': 'Exterior'},
        {'name': 'Pista de Tenis', 'number_of_facilities': 2, 'description': 'Una pista de tenis bien mantenida.', 'hour_price': 30.0, 'facility_type': 'Exterior'}
    ]

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
            photo = Photo.objects.create(activity=activity, image=f"activities/{activity.id}/{image_file}")
            print(f'Added image {photo.image} to activity {activity.name}')

        for bon in bonuses:
            bonus = Bonus.objects.create(
                activity = activity,
                bonus_type = bon['bonus_type'],
                price = bon['price'],
            )
            print(bonus)

        sessions_act = create_sessions(schedules, activity)

    # Create facilities and assign schedules
    for fac in facilities:
        facility = SportFacility.objects.create(
            name=fac['name'],
            number_of_facilities=fac['number_of_facilities'],
            description=fac['description'],
            hour_price=fac['hour_price'],
            facility_type=fac['facility_type']
        )

        schedules = []
        for day, hours in facility_schedules.get(facility.name, {}).items():
            schedules.extend(create_schedule(day, hours))

        facility.schedules.set(schedules)

        # Associate existing images
        facility_images_folder = f'media/facilities/{facility.id}'
        image_files = get_images_from_folder(facility_images_folder)

        for image_file in image_files:
            photo = Photo.objects.create(facility=facility, image=f"facilities/{facility.id}/{image_file}")
            print(f'Added image {photo.image} to facility {facility.name}')

        sesions_fac = create_sessions(schedules, facility=facility)


    print(sessions_act)
    print(sesions_fac)

    print("Population completed!")

if __name__ == '__main__':
    print("Starting application population script...")
    populate()
    print("Done!")
