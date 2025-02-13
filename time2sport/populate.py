import django
import os
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'time2sport.settings')
django.setup()

from gestion_deportiva.models import SportFacility, Activity, Schedule, Photo

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

def populate():
    activity_schedules = {
        'Football Match': {
            'Monday': [('08:00:00', '09:00:00'), ('11:00:00', '12:00:00')],
            'Tuesday': [('09:00:00', '11:00:00')],
            'Friday': [('08:00:00', '10:00:00')]
        },
        'Tennis Training': {
            'Monday': [('10:00:00', '12:00:00')],
            'Wednesday': [('14:00:00', '16:00:00')],
            'Saturday': [('09:00:00', '11:00:00')]
        },
        'Basketball Training': {
            'Thursday': [('17:00:00', '19:00:00')],
            'Sunday': [('10:00:00', '12:00:00')]
        },
        'Swimming Lesson': {
            'Monday': [('07:00:00', '08:00:00')],
            'Wednesday': [('15:00:00', '16:00:00')],
            'Friday': [('18:00:00', '19:30:00')]
        },
        'Running Workout': {
            'Tuesday': [('06:00:00', '07:00:00'), ('19:00:00', '20:00:00')],
            'Thursday': [('08:00:00', '09:00:00')]
        }
    }

    facility_schedules = {
        'Football Field': {
            'Monday': [('07:00:00', '10:00:00')],
            'Wednesday': [('12:00:00', '15:00:00')],
            'Saturday': [('10:00:00', '12:00:00')]
        },
        'Tennis Court': {
            'Tuesday': [('08:00:00', '10:00:00')],
            'Thursday': [('16:00:00', '18:00:00')],
            'Sunday': [('09:00:00', '11:00:00')]
        }
    }

    activities = [
        {'name': 'Football Match', 'location': 'Football Field', 'description': 'A football match with teams.', 'activity_type': 'Terrestrial'},
        {'name': 'Tennis Training', 'location': 'Tennis Court', 'description': 'Tennis practice session.', 'activity_type': 'Terrestrial'},
        {'name': 'Basketball Training', 'location': 'Basketball Court', 'description': 'Basketball skills training.', 'activity_type': 'Terrestrial'},
        {'name': 'Swimming Lesson', 'location': 'Swimming Pool', 'description': 'Swimming lessons for all levels.', 'activity_type': 'Aquatic'},
        {'name': 'Running Workout', 'location': 'Running Track', 'description': 'Cardio workout session.', 'activity_type': 'Terrestrial'}
    ]

    facilities = [
        {'name': 'Football Field', 'numberOf_facilities': 2, 'description': 'A large outdoor football field.', 'hour_price': 50.0, 'facility_type': 'Outside'},
        {'name': 'Tennis Court', 'numberOf_facilities': 2, 'description': 'A well-maintained tennis court.', 'hour_price': 30.0, 'facility_type': 'Outside'}
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

    # Create facilities and assign schedules
    for fac in facilities:
        facility = SportFacility.objects.create(
            name=fac['name'],
            numberOf_facilities=fac['numberOf_facilities'],
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

    print("Population completed!")

if __name__ == '__main__':
    print("Starting application population script...")
    populate()
    print("Done!")
