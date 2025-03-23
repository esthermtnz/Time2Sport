from django.test import TestCase, Client
from django.urls import reverse
from gestion_deportiva.models import Activity, SportFacility, Schedule, Bonus, User

class SearchResultsViewTestCase(TestCase):
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

        #Create a bonus
        cls.bonus = Bonus.objects.create(
            activity=cls.activity,
            bonus_type="annual",
            price=100.00
        )

        #Create a user
        cls.user = User.objects.create_user(
            username = "username",
            password = "password",
            is_uam = True,
            user_type = "student"
        )

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