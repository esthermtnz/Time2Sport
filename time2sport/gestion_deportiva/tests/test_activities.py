from django.test import TestCase
from django.urls import reverse
from gestion_deportiva.models import Activity, SportFacility, Schedule, Bonus, User
from django.core.files.uploadedfile import SimpleUploadedFile


class AllActivitiesViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create an activity schedule
        cls.activity_schedule = Schedule.objects.create(
            day_of_week = "Tuesday",
            hour_begin = "08:00:00",
            hour_end = "14:00:00"
        )

        # Create an activity
        cls.activity = Activity.objects.create(
            name = "Zumba",
            location = "Sala 4",
            description = "Zumba coreografiada para jóvenes",
            activity_type = "terrestre",
        )
        cls.activity.schedules.add(cls.activity_schedule)

        #Create a user
        cls.user = User.objects.create_user(
            username = "username",
            password = "password",
            is_uam = True,
            user_type = "student"
        )

    def test_all_activities_view(self):
        self.client.force_login(self.user)

        #-- View verification --
        response = self.client.get(reverse('all_activities'))

        #Check that the template is correctly loaded
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'gestion_deportiva/activities/all_activities.html')
        
        #Check that activities is sent to the template
        self.assertIn(self.activity, response.context['activities'])

        #-- Template verification --
        #Check template data
        self.assertContains(response, 'Actividades Disponibles')
        self.assertContains(response, self.activity.name)
        self.assertContains(response, self.activity.location)
        self.assertContains(response, self.activity.get_activity_type_display())

        #Check that the activity schedule is displayed
        for schedule in self.activity.schedules.all():
            self.assertContains(response, schedule.get_day_of_week_display())
            self.assertContains(response, schedule.hour_begin.strftime("%H:%M"))
            self.assertContains(response, schedule.hour_end.strftime("%H:%M"))

        #Check that the 'REservar' button is displayed and redirects to activity details
        reservar_btn = reverse('activity_detail', args=[self.activity.id])
        self.assertContains(response, f'href="{reservar_btn}"')

        #Check that the activity contains a custom or default image
        if self.activity.photos.exists():
            self.assertContains(response, self.activity.photos.first().image.url)
        else:
            self.assertContains(response, '/static/gestion_deportiva/default-activity.jpg')
    

class ActivityDetailViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a sport facility schedule
        cls.sport_facility_schedule = Schedule.objects.create(
            day_of_week = "Wednesday",
            hour_begin = "09:00:00",
            hour_end = "11:00:00"
        )

        # Create an activity schedule
        cls.activity_schedule = Schedule.objects.create(
            day_of_week = "Tuesday",
            hour_begin = "08:00:00",
            hour_end = "14:00:00"
        )

        # Create a sport facility
        cls.sport_facility = SportFacility.objects.create(
            name = "Campo de Fútbol",
            number_of_facilities = 2,
            description = "Campo de fútbol sala para fútbol 5",
            hour_price = 25.0,
            facility_type = "exterior"
        )
        cls.sport_facility.schedules.add(cls.sport_facility_schedule)

        # Create an activity
        cls.activity = Activity.objects.create(
            name = "Zumba",
            location = "Sala 4",
            description = "Zumba coreografiada para jóvenes",
            activity_type = "terrestre",
        )
        cls.activity.schedules.add(cls.activity_schedule)

        #Create a user
        cls.user = User.objects.create_user(
            username = "username",
            password = "password",
            is_uam = True,
            user_type = "student"
        )

    def test_activity_detail_view(self):
        self.client.force_login(self.user)


        #-- View verification --
        response = self.client.get(reverse('activity_detail', args=[self.activity.id]))
        
        #Check that the template is correctly loaded
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'gestion_deportiva/activities/activity_detail.html')
        
        #Check that the activity is sent to the template
        self.assertEqual(self.activity, response.context['activity'])

        #-- Template verification --
        #Check template data
        self.assertContains(response, self.activity.name)

        #Check that the activity schedule is displayed
        for schedule in self.activity.schedules.all():
            self.assertContains(response, schedule.get_day_of_week_display())
            self.assertContains(response, schedule.hour_begin.strftime("%H:%M"))
            self.assertContains(response, schedule.hour_end.strftime("%H:%M"))

        self.assertContains(response, self.activity.location)
        self.assertContains(response, self.activity.get_activity_type_display())
        self.assertContains(response, self.activity.description)

        #Check that the 'Inscribirse' button is displayed
        self.assertContains(response, '<button class="btn btn-success btn-lg">INSCRIBIRSE</button>', html=True)

        #Check that the activity's photos are displayed
        if self.activity.photos.exists():
            for photo in self.activity.photos.all:
                self.assertContains(response, photo.image.url)
        else:
            self.assertNotContains(response, '<img src="', html=True)