from django.test import TestCase
from django.urls import reverse
from sbai.models import Activity, SportFacility, Schedule, DayOfWeek
from sgu.models import User


class SchedulesViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a sport facility schedule
        cls.sport_facility_schedule = Schedule.objects.create(
            day_of_week=DayOfWeek.MIERCOLES,
            hour_begin="09:00:00",
            hour_end="11:00:00"
        )

        # Create an activity schedule
        cls.activity_schedule = Schedule.objects.create(
            day_of_week=DayOfWeek.MARTES,
            hour_begin="08:00:00",
            hour_end="14:00:00"
        )

        # Create a sport facility
        cls.sport_facility = SportFacility.objects.create(
            name="Campo de Fútbol",
            number_of_facilities=2,
            description="Campo de fútbol sala para fútbol 5",
            hour_price=25.0,
            facility_type="exterior"
        )
        cls.sport_facility.schedules.add(cls.sport_facility_schedule)

        # Create an activity
        cls.activity = Activity.objects.create(
            name="Zumba",
            location="Sala 4",
            description="Zumba coreografiada para jóvenes",
            activity_type="terrestre",
        )
        cls.activity.schedules.add(cls.activity_schedule)

        # Create a user
        cls.user = User.objects.create_user(
            username="username",
            password="password",
            is_uam=True,
            user_type="student"
        )

    def test_redirect_for_unauthenticated_users(self):
        """Verifies that the user is logged in if it is not, redirects to login"""
        response = self.client.get(reverse('schedules'))
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(
            response, f"/accounts/login/?next={reverse('schedules')}")

    def test_schedules_view(self):
        """Ensures that the content of the schedules template is correct"""
        self.client.force_login(self.user)

        # -- View verification --
        response = self.client.get(reverse('schedules'))

        # Check that the schedules template is correctly loaded
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'schedules/schedules.html')

        # -- Template verification --
        # Check template data
        self.assertContains(response, 'Horarios')

        # CHeck activities schedules is correctly displayed
        self.assertContains(response, reverse('activities_schedule'))
        self.assertContains(response, 'Horarios Actividades', html=True)

        # Check fecility schedules is correctly displayed
        self.assertContains(response, reverse('facilities_schedule'))
        self.assertContains(response, 'Horarios Instalaciones', html=True)


class FacilitiesScheduleViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a sport facility schedule
        cls.sport_facility_schedule = Schedule.objects.create(
            day_of_week=DayOfWeek.MIERCOLES,
            hour_begin="09:00:00",
            hour_end="11:00:00"
        )

        # Create a sport facility
        cls.sport_facility = SportFacility.objects.create(
            name="Campo de Fútbol",
            number_of_facilities=2,
            description="Campo de fútbol sala para fútbol 5",
            hour_price=25.0,
            facility_type="exterior"
        )
        cls.sport_facility.schedules.add(cls.sport_facility_schedule)

        # Create a user
        cls.user = User.objects.create_user(
            username="username",
            password="password",
            is_uam=True,
            user_type="student"
        )

    def test_redirect_for_unauthenticated_users(self):
        """Verifies that the user is logged in if it is not, redirects to login"""
        response = self.client.get(reverse('facilities_schedule'))
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(
            response, f"/accounts/login/?next={reverse('facilities_schedule')}")

    def test_facilities_schedule_view(self):
        """Ensures that the facilities schedules view is correctly displayed"""
        self.client.force_login(self.user)

        # -- View verification --
        response = self.client.get(reverse('facilities_schedule'))

        # Check that the facilities_schedule template is correctly loaded
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'schedules/facilities_schedule.html')

        # Check the facility is sent to the template
        self.assertIn(self.sport_facility, response.context['facilities'])

        # -- Template verification --
        # Descargar button exists and redirects to download_facilities_schedule
        self.assertContains(response, reverse('download_facilities_schedule'))
        self.assertContains(response, 'Descargar PDF')

        # Schedule data
        self.assertContains(response, 'Horarios de Instalaciones')
        self.assertContains(response, 'Actividad')
        self.assertContains(response, 'Día')
        self.assertContains(response, 'Horario')
        self.assertContains(response, self.sport_facility.name)

        # Check that the facility schedules are displayed
        for schedule in self.sport_facility.schedules.all():
            self.assertContains(response, schedule.get_day_of_week_display())
            self.assertContains(
                response, schedule.hour_begin.strftime("%H:%M"))
            self.assertContains(response, schedule.hour_end.strftime("%H:%M"))


class ActivitiesScheduleViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create an activity schedule
        cls.activity_schedule = Schedule.objects.create(
            day_of_week=DayOfWeek.MARTES,
            hour_begin="08:00:00",
            hour_end="14:00:00"
        )

        # Create an activity
        cls.activity = Activity.objects.create(
            name="Zumba",
            location="Sala 4",
            description="Zumba coreografiada para jóvenes",
            activity_type="terrestre",
        )
        cls.activity.schedules.add(cls.activity_schedule)

        # Create a user
        cls.user = User.objects.create_user(
            username="username",
            password="password",
            is_uam=True,
            user_type="student"
        )

    def test_redirect_for_unauthenticated_users(self):
        """Verifies that the user is logged in if it is not, redirects to login"""
        response = self.client.get(reverse('schedules'))
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(
            response, f"/accounts/login/?next={reverse('schedules')}")

    def test_activities_schedule_view(self):
        """Ensures that the activities schedules view is ocrrectly displayed"""
        self.client.force_login(self.user)

        # -- View verification --
        response = self.client.get(reverse('activities_schedule'))

        # Check that the activities_schedule template is correctly loaded
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'schedules/activities_schedule.html')

        # Check the activity is sent to the template
        formatted_schedules = [
            {
                "day": schedule.get_day_of_week_display(),
                "times": f"{schedule.hour_begin.strftime('%H:%M')} - {schedule.hour_end.strftime('%H:%M')}"
            }
            for schedule in self.activity.schedules.all()
        ]

        grouped_schedules = [
            {
                "name": self.activity.name,
                "schedules": formatted_schedules
            }
        ]

        self.assertEqual(grouped_schedules, response.context['activities'])

        # -- Template verification --
        # Descargar button exists and redirects to download_activities_schedule
        self.assertContains(response, reverse('download_activities_schedule'))
        self.assertContains(response, 'Descargar PDF')

        # Schedule data
        self.assertContains(response, 'Horarios de Actividades')
        self.assertContains(response, 'Actividad')
        self.assertContains(response, 'Día')
        self.assertContains(response, 'Horario')
        self.assertContains(response, self.activity.name)

        # Check that the activity schedules are displayed
        for schedule in self.activity.schedules.all():
            self.assertContains(response, schedule.get_day_of_week_display())
            self.assertContains(
                response, schedule.hour_begin.strftime("%H:%M"))
            self.assertContains(response, schedule.hour_end.strftime("%H:%M"))


class DownloadsViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a sport facility schedule
        cls.sport_facility_schedule = Schedule.objects.create(
            day_of_week=DayOfWeek.MIERCOLES,
            hour_begin="09:00:00",
            hour_end="11:00:00"
        )

        # Create an activity schedule
        cls.activity_schedule = Schedule.objects.create(
            day_of_week=DayOfWeek.MARTES,
            hour_begin="08:00:00",
            hour_end="14:00:00"
        )

        # Create a sport facility
        cls.sport_facility = SportFacility.objects.create(
            name="Campo de Fútbol",
            number_of_facilities=2,
            description="Campo de fútbol sala para fútbol 5",
            hour_price=25.0,
            facility_type="Exterior"
        )
        cls.sport_facility.schedules.add(cls.sport_facility_schedule)

        # Create an activity
        cls.activity = Activity.objects.create(
            name="Zumba",
            location="Sala 4",
            description="Zumba coreografiada para jóvenes",
            activity_type="Terrestre",
        )
        cls.activity.schedules.add(cls.activity_schedule)

        # Create a user
        cls.user = User.objects.create_user(
            username="username",
            password="password",
            is_uam=True,
            user_type="student"
        )

    def test_download_facilities_schedule_view(self):
        """Ensures that the facilities schedules pdf is generated"""
        self.client.force_login(self.user)

        # CHeck that the download_facilities_schedule is called correctly
        response = self.client.get(reverse('download_facilities_schedule'))
        self.assertEqual(response.status_code, 200)

        # Check that it generates a correct pdf document
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('attachment; filename="facilities_schedule.pdf"',
                      response['Content-Disposition'])

    def test_download_activities_schedule_view(self):
        """Ensures that the activity schedules pdf is generated"""
        self.client.force_login(self.user)

        # Check that the download_activities_schedule is called correctly
        response = self.client.get(reverse('download_activities_schedule'))
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('attachment; filename="activities_schedule.pdf"',
                      response['Content-Disposition'])
