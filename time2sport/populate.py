import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'time2sport.settings')
django.setup()

from gestion_deportiva.models import SportFacility, Activity, Schedule, Photo

def get_images_from_folder(folder_path):
    """Returns a list of image file names from a given folder."""
    if not os.path.exists(folder_path):
        return []
    return [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

def populate():
    schedules = [
        {'day_of_week': 'Monday', 'hour_begin': '08:00:00', 'hour_end': '10:00:00'},
        {'day_of_week': 'Tuesday', 'hour_begin': '09:00:00', 'hour_end': '11:00:00'},
        {'day_of_week': 'Friday', 'hour_begin': '08:00:00', 'hour_end': '10:00:00'}
    ]

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

    # Create schedules
    created_schedules = []
    for sch in schedules:
        schedule = Schedule.objects.create(
            day_of_week=sch['day_of_week'],
            hour_begin=sch['hour_begin'],
            hour_end=sch['hour_end']
        )
        created_schedules.append(schedule)

    # Create activities
    for act in activities:
        activity = Activity.objects.create(
            name=act['name'],
            location=act['location'],
            description=act['description'],
            activity_type=act['activity_type']
        )

        # Assign schedules to activities
        activity.schedules.set(created_schedules)

        # Associate existing image paths
        activity_images_folder = f'media/activities/{activity.id}'
        image_files = get_images_from_folder(activity_images_folder)

        for image_file in image_files:
            photo = Photo.objects.create(activity=activity, image=f"activities/{activity.id}/{image_file}")
            print(f'Added image {photo.image} to activity {activity.name}')

    # Create facilities
    for fac in facilities:
        facility = SportFacility.objects.create(
            name=fac['name'],
            numberOf_facilities=fac['numberOf_facilities'],
            description=fac['description'],
            hour_price=fac['hour_price'],
            facility_type=fac['facility_type']
        )

        # Associate existing image paths
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
