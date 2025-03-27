from django.test import TestCase, Client
from django.urls import reverse
from sbai.models import Activity, SportFacility, Schedule, Bonus
from sgu.models import User


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
            facility_type = "Exterior"
        )
        cls.sport_facility.schedules.add(cls.sport_facility_schedule)

        # Create an activity
        cls.activity = Activity.objects.create(
            name = "Zumba",
            location = "Sala 4",
            description = "Zumba coreografiada para jóvenes",
            activity_type = "Terrestre",
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
    
    def test_redirect_for_unauthenticated_users(self):
        """Ensure search requires authentication"""
        response = self.client.get(reverse('search_results'))
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(response, f"/accounts/login/?next={reverse('search_results')}")


    def test_search_results_view_1(self):
        """Searching an activity with filters"""
        self.client.force_login(self.user)

        #-- View verification --
        #(POST) - Post the query searching for an activity
        response = self.client.post(reverse('search_results'), {'q': self.activity.name, 'category': self.activity.activity_type})
        
        #Check that the query is posted to search_results template
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'search_results.html')

        self.assertContains(response, f'Searching "{self.activity.name}"')

        #(GET) - Get the template search_results searching for an activity
        response = self.client.get(reverse('search_results'))
        #Check that the query is gotten to search_results template
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'search_results.html')

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
        self.assertTemplateUsed(response, 'search_results.html')

        self.assertContains(response, f'Searching "{self.sport_facility.name}"')

        #(GET) - Get the template search_results searching for an sport facility
        response = self.client.get(reverse('search_results'))
        #Check that the query is gotten to search_results template
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'search_results.html')

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
        self.assertTemplateUsed(response, 'search_results.html')

        self.assertContains(response, f'Searching ""')

        #(GET) - Get the template search_results searching for an sport facility
        response = self.client.get(reverse('search_results'))
        #Check that the query is gotten to search_results template
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'search_results.html')

        #Check that the sport facility is in the template
        self.assertIn(self.sport_facility, response.context['facilities'])
        self.assertIn(self.activity, response.context['activities'])

        #-- Template verification --
        self.assertContains(response, "Instalaciones")
        self.assertContains(response, f'{self.sport_facility.name} - {self.sport_facility.description}')
        
        self.assertContains(response, "Actividades")
        self.assertContains(response, f'{self.activity.name} - {self.activity.description}')

    def test_search_no_results(self):
        """Searching for a non-existent activity or facility"""
        self.client.force_login(self.user)

        response = self.client.post(reverse('search_results'), {'q': "Busqueda incorrecta"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No se encontraron instalaciones.")
        self.assertContains(response, "No se encontraron actividades.")

    def test_search_case_insensitive(self):
        """Searching with different letter cases"""
        self.client.force_login(self.user)

        response = self.client.post(reverse('search_results'), {'q': "zUmBa"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'Searching "zUmBa"')

        #(GET) - Get the template search_results searching for an activity
        response = self.client.get(reverse('search_results'))
        #Check that the query is gotten to search_results template
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'search_results.html')

        #Check that the activity is in the template
        self.assertIn(self.activity, response.context['activities'])

        #-- Template verification --
        self.assertContains(response, "Actividades")
        self.assertContains(response, f'{self.activity.name} - {self.activity.description}')

    def test_search_with_extra_spaces(self):
        """Searching with extra spaces"""
        self.client.force_login(self.user)

        response = self.client.post(reverse('search_results'), {'q': "  Zumba  "})

        self.assertEqual(response.status_code, 200)
        self.assertIn(self.activity, response.context['activities'])

    def test_search_filter_by_category(self):
        """Searching by category"""
        self.client.force_login(self.user)

        # Buscar solo actividades terrestres
        response = self.client.post(reverse('search_results'), {'category': "terrestre"})
        self.assertEqual(response.status_code, 200)

        self.assertIn(self.activity, response.context['activities'])
        self.assertIsNone(response.context['facilities'])