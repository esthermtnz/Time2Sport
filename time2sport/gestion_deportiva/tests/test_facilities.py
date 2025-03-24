from django.test import TestCase
from django.urls import reverse
from gestion_deportiva.models import SportFacility, Schedule, User


class AllFacilitiesViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a sport facility schedule
        cls.sport_facility_schedule = Schedule.objects.create(
            day_of_week = "Wednesday",
            hour_begin = "09:00:00",
            hour_end = "11:00:00"
        )

        # Create a sport facility
        cls.sport_facility = SportFacility.objects.create(
            name = "Campo de Fútbol",
            number_of_facilities = 2,
            description = "Campo de fútbol sala para fútbol 5",
            hour_price = 25.0,
            facility_type = "Exterior"
        )
        cls.sport_facility.schedules.add(cls.sport_facility_schedule)

        #Create a user
        cls.user = User.objects.create_user(
            username = "username",
            password = "password",
            is_uam = True,
            user_type = "student"
        )

    def test_all_facilities_view(self):

        self.client.force_login(self.user)

        #-- View verification --
        response = self.client.get(reverse('all_facilities'))

        #Check that the template is correctly loaded
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'gestion_deportiva/facilities/all_facilities.html')
        
        #Check the facility is sent to the template
        self.assertIn(self.sport_facility, response.context['facilities'])

        #-- Template verification --
        self.assertContains(response, 'Instalaciones Deportivas')
        self.assertContains(response, self.sport_facility.name)
        self.assertContains(response, self.sport_facility.get_facility_type_display())
        self.assertContains(response, self.sport_facility.hour_price)
        self.assertContains(response, self.sport_facility.number_of_facilities)

        #Check that the facility schedule is displayed
        for schedule in self.sport_facility.schedules.all():
            self.assertContains(response, schedule.get_day_of_week_display())
            self.assertContains(response, schedule.hour_begin.strftime("%H:%M"))
            self.assertContains(response, schedule.hour_end.strftime("%H:%M"))

        #Check that the 'Reservar' button is displayed and redirects to facility details
        reservar_btn = reverse('facility_detail', args=[self.sport_facility.id])
        self.assertContains(response, f'href="{reservar_btn}"')

        #Check that the facility contains a custom or default image
        if self.sport_facility.photos.exists():
            self.assertContains(response, self.sport_facility.photos.first().image.url)
        else:
            self.assertContains(response, '/static/gestion_deportiva/default-facility.png')

class FacilityDetailViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a sport facility schedule
        cls.sport_facility_schedule = Schedule.objects.create(
            day_of_week = "Wednesday",
            hour_begin = "09:00:00",
            hour_end = "11:00:00"
        )

        # Create a sport facility
        cls.sport_facility = SportFacility.objects.create(
            name = "Campo de Fútbol",
            number_of_facilities = 2,
            description = "Campo de fútbol sala para fútbol 5",
            hour_price = 25.0,
            facility_type = "Exterior"
        )
        cls.sport_facility.schedules.add(cls.sport_facility_schedule)

        #Create a user
        cls.user = User.objects.create_user(
            username = "username",
            password = "password",
            is_uam = True,
            user_type = "student"
        )
    
        
    def test_facility_detail_view(self):

        self.client.force_login(self.user)


        #-- View verification --
        response = self.client.get(reverse('facility_detail', args=[self.sport_facility.id]))
        
        #Check that the template is correctly loaded
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'gestion_deportiva/facilities/facility_detail.html')
        
        #-- Template verification --
        #Check template data
        self.assertContains(response, self.sport_facility.name)
        self.assertContains(response, self.sport_facility.get_facility_type_display())
        self.assertContains(response, self.sport_facility.hour_price)
        self.assertContains(response, self.sport_facility.number_of_facilities)

        #Check that the facility schedule is displayed
        for schedule in self.sport_facility.schedules.all():
            self.assertContains(response, schedule.get_day_of_week_display())
            self.assertContains(response, schedule.hour_begin.strftime("%H:%M"))
            self.assertContains(response, schedule.hour_end.strftime("%H:%M"))

        self.assertContains(response, self.sport_facility.description)

        #Check that the 'Reservar' button is displayed
        self.assertContains(response, '<button class="btn btn-success btn-lg">RESERVAR</button>', html=True)

        #Check that the facility's photos are displayed
        if self.sport_facility.photos.exists():
            for photo in self.sport_facility.photos.all:
                self.assertContains(response, photo.image.url)
        else:
            self.assertNotContains(response, '<img src="', html=True)