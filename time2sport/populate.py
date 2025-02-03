import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'time2sport.settings')
django.setup()

from gestion_deportiva.models import SportFacility, Activity, Schedule, Photo

from django.core.files import File


def populate():
    schedules = [
        {'day_of_week': 'Monday', 'hour_begin': '08:00:00', 'hour_end': '10:00:00'},
        {'day_of_week': 'Tuesday', 'hour_begin': '09:00:00', 'hour_end': '11:00:00'},
        {'day_of_week': 'Friday', 'hour_begin': '08:00:00', 'hour_end': '10:00:00'},
    ]


    facilities = [
        {'name': 'Football Field', 'numberOf_facilities': 2, 'description': 'A large outdoor football field.', 'hour_price': 50.0, 'facility_type': 'Outside'},
        {'name': 'Tennis Court', 'numberOf_facilities': 2, 'description': 'A well-maintained tennis court.', 'hour_price': 30.0, 'facility_type': 'Outside'},
        {'name': 'Basketball Court', 'numberOf_facilities': 3, 'description': 'A professional basketball court.', 'hour_price': 40.0, 'facility_type': 'Inside'},
        {'name': 'Swimming Pool', 'numberOf_facilities': 1, 'description': 'A large Olympic-sized swimming pool.', 'hour_price': 60.0, 'facility_type': 'Inside'},
        {'name': 'Running Track', 'numberOf_facilities': 1, 'description': 'An outdoor running track.', 'hour_price': 20.0, 'facility_type': 'Outside'},
    ]

    activities = [
        {'name': 'Football Match', 'location': 'Football Field', 'description': 'A football match with teams.', 'activity_type': 'Terrestrial'},
        {'name': 'Tennis Training', 'location': 'Tennis Court', 'description': 'Tennis practice session.', 'activity_type': 'Terrestrial'},
        {'name': 'Basketball Training', 'location': 'Basketball Court', 'description': 'Basketball skills training.', 'activity_type': 'Terrestrial'},
        {'name': 'Swimming Lesson', 'location': 'Swimming Pool', 'description': 'Swimming lessons for all levels.', 'activity_type': 'Aquatic'},
        {'name': 'Running Workout', 'location': 'Running Track', 'description': 'Cardio workout session.', 'activity_type': 'Terrestrial'},
        {'name': 'Yoga Class', 'location': 'Yoga Hall', 'description': 'A relaxing yoga session.', 'activity_type': 'Terrestrial'},
        {'name': 'Cycling Session', 'location': 'Cycling Track', 'description': 'Cycling session for beginners.', 'activity_type': 'Terrestrial'},
        {'name': 'Boxing Class', 'location': 'Boxing Arena', 'description': 'Boxing class for fitness.', 'activity_type': 'Terrestrial'},
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

    # Create facilities
    created_facilities = []
    for fac in facilities:
        facility = SportFacility.objects.create(
            name=fac['name'],
            numberOf_facilities=fac['numberOf_facilities'],
            description=fac['description'],
            hour_price=fac['hour_price'],
            facility_type=fac['facility_type']
        )
        # Assign schedules to the facility
        for schedule in created_schedules:
            facility.add_schedule(schedule)
        created_facilities.append(facility)

    # Create activities
    created_activities = []
    for act in activities:
        activity = Activity.objects.create(
            name=act['name'],
            location=act['location'],
            description=act['description'],
            activity_type=act['activity_type']
        )
        # Assign schedules to the activity
        for schedule in created_schedules:
            activity.add_schedule(schedule)
        created_activities.append(activity)

    # Create photos (Example, assuming you have photo files in your media directory)
    # These should be real images for the actual implementation
    facility_photo = Photo.objects.create(image='image1.jpg')
    # activity_photo = Photo.objects.create(image='balon-de-futbol.jpg')
    with open('media/activities/1/balon-de-futbol.jpg', 'rb') as f:
        activity_photo = Photo.objects.create(activity=created_activities[0], image=File(f, name='balon-de-futbol.jpg'))
    created_activities[0].add_photo(activity_photo)


    # print path to image
    print(activity_photo.image.url)
    print(activity_photo.image.path)

    # Add photos to facilities
    for facility in created_facilities:
        facility.add_photo(facility_photo)

    # Add photos to activities
    # for activity in created_activities:
    #     activity.add_photo(activity_photo)

    print("Population completed!")


if __name__ == '__main__':
    print("Starting application population script...")
    populate()
    print("Done!")
