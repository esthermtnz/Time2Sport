from django.test import TestCase, Client
from django.urls import reverse
from gestion_deportiva.models import Activity, SportFacility, Schedule, Bonus, User
from django.core.files.uploadedfile import SimpleUploadedFile

class ViewsTestCase(TestCase):
    def setUp(self):
        # Create a sport facility schedule
        self.sport_facility_schedule = Schedule.objects.create(
            day_of_week = "Wednesday",
            hour_begin = "09:00:00",
            hour_end = "11:00:00"
        )

        # Create an activity schedule
        self.activity_schedule = Schedule.objects.create(
            day_of_week = "Tuesday",
            hour_begin = "08:00:00",
            hour_end = "14:00:00"
        )

        # Create a sport facility
        self.sport_facility = SportFacility.objects.create(
            name = "Campo de Fútbol",
            number_of_facilities = 2,
            description = "Campo de fútbol sala para fútbol 5",
            hour_price = 25.0,
            facility_type = "exterior"
        )
        self.sport_facility.schedules.add(self.sport_facility_schedule)

        # Create an activity
        self.activity = Activity.objects.create(
            name = "Zumba",
            location = "Sala 4",
            description = "Zumba coreografiada para jóvenes",
            activity_type = "terrestre",
        )
        self.activity.schedules.add(self.activity_schedule)

        #Create a bonus
        self.bonus = Bonus.objects.create(
            activity=self.activity,
            bonus_type="annual",
            price=100.00
        )

        #Create a user
        self.user = User.objects.create_user(
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

    def test_schedules_view(self):

        self.client.force_login(self.user)


        #-- View verification --
        response = self.client.get(reverse('schedules'))

        #Check that the schedules template is correctly loaded
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'gestion_deportiva/schedules/schedules.html')
    
        #-- Template verification --
        #Check template data
        self.assertContains(response, 'Horarios')

        #CHeck activities schedules is correctly displayed
        self.assertContains(response, reverse('activities_schedule'))
        self.assertContains(response, 'Horarios Actividades', html=True)

        #Check fecility schedules is correctly displayed
        self.assertContains(response, reverse('facilities_schedule'))
        self.assertContains(response, 'Horarios Instalaciones', html=True)

    def test_facilities_schedule_view(self):

        self.client.force_login(self.user)


        #-- View verification --
        response = self.client.get(reverse('facilities_schedule'))

        #Check that the facilities_schedule template is correctly loaded
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'gestion_deportiva/schedules/facilities_schedule.html')

        #Check the facility is sent to the template
        self.assertIn(self.sport_facility, response.context['facilities'])

        #-- Template verification --
        #Descargar button exists and redirects to download_facilities_schedule
        self.assertContains(response, reverse('download_facilities_schedule'))
        self.assertContains(response, 'Descargar PDF')

        #Schedule data
        self.assertContains(response, 'Horarios de Instalaciones')
        self.assertContains(response, 'Actividad')
        self.assertContains(response, 'Día')
        self.assertContains(response, 'Horario')
        self.assertContains(response, self.sport_facility.name)

        #Check that the facility schedules are displayed
        for schedule in self.sport_facility.schedules.all():
            self.assertContains(response, schedule.get_day_of_week_display())
            self.assertContains(response, schedule.hour_begin.strftime("%H:%M"))
            self.assertContains(response, schedule.hour_end.strftime("%H:%M"))

    def test_activities_schedule_view(self):

        self.client.force_login(self.user)


        #-- View verification --
        response = self.client.get(reverse('activities_schedule'))

        #Check that the activities_schedule template is correctly loaded
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'gestion_deportiva/schedules/activities_schedule.html')

        #Check the activity is sent to the template
        formatted_schedules = [
            {
                "day": schedule.day_of_week,
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

        #-- Template verification --
        #Descargar button exists and redirects to download_activities_schedule
        self.assertContains(response, reverse('download_activities_schedule'))
        self.assertContains(response, 'Descargar PDF')

        #Schedule data
        self.assertContains(response, 'Horarios de Actividades')
        self.assertContains(response, 'Actividad')
        self.assertContains(response, 'Día')
        self.assertContains(response, 'Horario')
        self.assertContains(response, self.activity.name)

        #Check that the activity schedules are displayed
        for schedule in self.activity.schedules.all():
            self.assertContains(response, schedule.get_day_of_week_display())
            self.assertContains(response, schedule.hour_begin.strftime("%H:%M"))
            self.assertContains(response, schedule.hour_end.strftime("%H:%M"))


    def test_download_facilities_schedule_view(self):

        self.client.force_login(self.user)


        #CHeck that the download_facilities_schedule is called correctly
        response = self.client.get(reverse('download_facilities_schedule'))
        self.assertEqual(response.status_code, 200)

        #Check that it generates a correct pdf document
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('attachment; filename="facilities_schedule.pdf"', response['Content-Disposition'])


    def test_download_activities_schedule_view(self):

        self.client.force_login(self.user)


        #Check that the download_activities_schedule is called correctly
        response = self.client.get(reverse('download_activities_schedule'))
        self.assertEqual(response.status_code, 200)


        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('attachment; filename="activities_schedule.pdf"', response['Content-Disposition'])


    def test_search_results_view_1(self):
        """Searching an activity with filters"""

        self.client.force_login(self.user)


        #-- View verification --

        #Post the query searching for an activity
        response = self.client.post(reverse('search_results'), {'q': self.activity.name, 'category': self.activity.activity_type})
        
        #Check that the query is posted to search_results template
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'gestion_deportiva/search_results.html')

        self.assertContains(response, f'Searching "{self.activity.name}"')

        #Get the template search_results searching for an activity
        response = self.client.get(reverse('search_results'))
        #Check that the query is gotten to search_results template
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'gestion_deportiva/search_results.html')

        #Check that the activity is in the template
        self.assertIn(self.activity, response.context['activities'])

        #-- Template verification --
        self.assertContains(response, "Actividades")
        self.assertContains(response, f'{self.activity.name} - {self.activity.description}')

    def test_search_results_view_2(self):
        """Searching a sport facility with filters"""

        self.client.force_login(self.user)


        #-- View verification --

        #(POST) - Post the query searching for a sport facility
        response = self.client.post(reverse('search_results'), {'q': self.sport_facility.name, 'category': self.sport_facility.facility_type})
        
        #Check that the query is posted to search_results template
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'gestion_deportiva/search_results.html')

        self.assertContains(response, f'Searching "{self.sport_facility.name}"')

        #(GET) - Get the template search_results searching for an sport facility
        response = self.client.get(reverse('search_results'))
        #Check that the query is gotten to search_results template
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'gestion_deportiva/search_results.html')

        #Check that the sport facility is in the template
        self.assertIn(self.sport_facility, response.context['facilities'])

        #-- Template verification --
        self.assertContains(response, "Instalaciones")
        self.assertContains(response, f'{self.sport_facility.name} - {self.sport_facility.description}')
        
    def test_search_results_view_3(self):
        """Searching an empty query without filters"""

        self.client.force_login(self.user)
    
        #-- View verification --

        #(POST) - Post the query searching for a sport facility
        response = self.client.post(reverse('search_results'), {'q': ""})
        
        #Check that the query is posted to search_results template
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'gestion_deportiva/search_results.html')

        self.assertContains(response, f'Searching ""')

        #(GET) - Get the template search_results searching for an sport facility
        response = self.client.get(reverse('search_results'))
        #Check that the query is gotten to search_results template
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'gestion_deportiva/search_results.html')

        #Check that the sport facility is in the template
        self.assertIn(self.sport_facility, response.context['facilities'])
        self.assertIn(self.activity, response.context['activities'])

        #-- Template verification --
        self.assertContains(response, "Instalaciones")
        self.assertContains(response, f'{self.sport_facility.name} - {self.sport_facility.description}')
        
        self.assertContains(response, "Actividades")
        self.assertContains(response, f'{self.activity.name} - {self.activity.description}')
        
