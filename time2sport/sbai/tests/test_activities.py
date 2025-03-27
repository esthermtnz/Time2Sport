from django.test import TestCase
from django.urls import reverse
from sbai.models import Activity, Schedule, Bonus
from sgu.models import User
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
            activity_type = "Terrestre",
        )
        cls.activity.schedules.add(cls.activity_schedule)

        # Create an activity with no schedule
        cls.activity_without_schedule = Activity.objects.create(
            name="Yoga",
            location="Sala 2",
            description="Clase de Yoga",
            activity_type="Terrestre",
        )

        #Create a user
        cls.user = User.objects.create_user(
            username = "username",
            password = "password",
            is_uam = True,
            user_type = "student"
        )

    def test_redirect_for_unauthenticated_users(self):
        "Verifies that the users ared logged in before accessing the template"
        response = self.client.get(reverse('all_activities'))
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(response, f"/accounts/login/?next={reverse('all_activities')}")

    def test_all_activities_view(self):
        "Ensures that the all activities template is correctly displayed"
        self.client.force_login(self.user)

        #-- View verification --
        response = self.client.get(reverse('all_activities'))

        #Check that the template is correctly loaded
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'activities/all_activities.html')
        
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

        #Check that the 'Reservar' button is displayed and redirects to activity details
        reservar_btn = reverse('activity_detail', args=[self.activity.id])
        self.assertContains(response, f'href="{reservar_btn}"')

        #Check that the activity contains a custom or default image
        if self.activity.photos.exists():
            self.assertContains(response, self.activity.photos.first().image.url)
        else:
            self.assertContains(response, '/static/default-activity.jpg')

    def test_activity_without_schedule(self):
        "Ensures that the activity without schedule is showed in the content"
        self.client.force_login(self.user)

        response = self.client.get(reverse('all_activities'))
        #Check that the template is correctly loaded
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'activities/all_activities.html')
        
        #Check that activities is sent to the template
        self.assertIn(self.activity_without_schedule, response.context['activities'])

        #-- Template verification --
        #Check template data
        self.assertContains(response, 'Actividades Disponibles')
        self.assertContains(response, self.activity_without_schedule.name)
        self.assertContains(response, self.activity_without_schedule.location)
        self.assertContains(response, self.activity_without_schedule.get_activity_type_display())

        #Check that the 'Reservar' button is displayed and redirects to activity_without_schedule details
        reservar_btn = reverse('activity_detail', args=[self.activity_without_schedule.id])
        self.assertContains(response, f'href="{reservar_btn}"')

        #Check that the activity_without_schedule contains a custom or default image
        if self.activity_without_schedule.photos.exists():
            self.assertContains(response, self.activity_without_schedule.photos.first().image.url)
        else:
            self.assertContains(response, '/static/default-activity.jpg')

    def test_multiple_activities(self):
        "ENsures that the 2 activities are showed in the template"
        self.client.force_login(self.user)
        response = self.client.get(reverse('all_activities'))

        #Check that the template is correctly loaded
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'activities/all_activities.html')
        
        #Check that activities is sent to the template
        self.assertIn(self.activity_without_schedule, response.context['activities'])
        self.assertIn(self.activity, response.context['activities'])
        
        #-- Template verification --
        #Check template data
        self.assertContains(response, 'Actividades Disponibles')

        self.assertContains(response, self.activity.name)
        self.assertContains(response, self.activity.location)
        self.assertContains(response, self.activity.get_activity_type_display())

        self.assertContains(response, self.activity_without_schedule.name)
        self.assertContains(response, self.activity_without_schedule.location)
        self.assertContains(response, self.activity_without_schedule.get_activity_type_display())

        #Check that the activity schedule is displayed
        for schedule in self.activity.schedules.all():
            self.assertContains(response, schedule.get_day_of_week_display())
            self.assertContains(response, schedule.hour_begin.strftime("%H:%M"))
            self.assertContains(response, schedule.hour_end.strftime("%H:%M"))

        #Check that the 'Reservar' button is displayed and redirects to activity details
        reservar_btn = reverse('activity_detail', args=[self.activity.id])
        self.assertContains(response, f'href="{reservar_btn}"')

        #Check that the 'Reservar' button is displayed and redirects to activity_without_schedule details
        reservar_btn = reverse('activity_detail', args=[self.activity_without_schedule.id])
        self.assertContains(response, f'href="{reservar_btn}"')

        #Check that the activity contains a custom or default image
        if self.activity.photos.exists():
            self.assertContains(response, self.activity.photos.first().image.url)
        else:
            self.assertContains(response, '/static/default-activity.jpg')

        #Check that the activity_without_schedule contains a custom or default image
        if self.activity_without_schedule.photos.exists():
            self.assertContains(response, self.activity_without_schedule.photos.first().image.url)
        else:
            self.assertContains(response, '/static/default-activity.jpg')

    def test_activity_uses_default_image(self):
        "Checks that if there is no image in the activity model, it loads the default one"
        self.client.force_login(self.user)
        response = self.client.get(reverse('all_activities'))
        self.assertContains(response, "/static/default-activity.jpg")



class ActivityDetailViewTestCase(TestCase):
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
            activity_type = "Terrestre",
        )
        cls.activity.schedules.add(cls.activity_schedule)

        # Create an activity with no schedule
        cls.activity_without_schedule = Activity.objects.create(
            name="Yoga",
            location="Sala 2",
            description="Clase de Yoga",
            activity_type="Terrestre",
        )

        cls.bonus1 = Bonus.objects.create(
            activity=cls.activity, 
            bonus_type="mensual", 
            price=30
        )
        cls.bonus2 = Bonus.objects.create(
            activity=cls.activity, 
            bonus_type="trimestral", 
            price=75
        )

        #Create a user
        cls.user = User.objects.create_user(
            username = "username",
            password = "password",
            is_uam = True,
            user_type = "student"
        )

    def test_redirect_for_unauthenticated_users(self):
        "Verifies that the user is logged in before accessing the template"
        response = self.client.get(reverse('activity_detail', args=[self.activity.id]))

        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(response, f'/accounts/login/?next=/activities/{self.activity.id}/')


    def test_activity_detail_view(self):
        "Ensures that the activity detail content is correct"
        self.client.force_login(self.user)

        #-- View verification --
        response = self.client.get(reverse('activity_detail', args=[self.activity.id]))
        
        #Check that the template is correctly loaded
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'activities/activity_detail.html')
        
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

        #Check that the bonuses are displayed
        for bonus in self.activity.bonuses.all():
            self.assertContains(response, f'{bonus.get_bonus_type_display()} - {bonus.price}€')

        #Check that the 'Inscribirse' button is displayed
        self.assertContains(response, '<button class="btn btn-success btn-lg">INSCRIBIRSE</button>', html=True)

        #Check that the activity's photos are displayed
        if self.activity.photos.exists():
            for photo in self.activity.photos.all:
                self.assertContains(response, photo.image.url)
        else:
            self.assertNotContains(response, '<img src="', html=True)
    
    def test_activity_without_schedule_detail(self):
        "Ensures that the details about the activity without schedule are correctly displayed"
        self.client.force_login(self.user)
        response = self.client.get(reverse('activity_detail', args=[self.activity_without_schedule.id]))

        #Check that the template is correctly loaded
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'activities/activity_detail.html')

        #Check that the activity_without_schedule is sent to the template
        self.assertEqual(self.activity_without_schedule, response.context['activity'])

        #-- Template verification --
        #Check template data
        self.assertContains(response, self.activity_without_schedule.name)
        self.assertContains(response, self.activity_without_schedule.location)
        self.assertContains(response, self.activity_without_schedule.get_activity_type_display())
        self.assertContains(response, self.activity_without_schedule.description)

        week = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        for day in week:
            self.assertNotContains(response, day)

        #Check that the 'Inscribirse' button is displayed
        self.assertContains(response, '<button class="btn btn-success btn-lg">INSCRIBIRSE</button>', html=True)

        #Check that the activity's photos are displayed
        if self.activity_without_schedule.photos.exists():
            for photo in self.activity_without_schedule.photos.all:
                self.assertContains(response, photo.image.url)
        else:
            self.assertNotContains(response, '<img src="', html=True)

    def test_activity_with_multiple_bonuses(self):
        "Ensures that the bonus selectors are correct"
        self.client.force_login(self.user)
        response = self.client.get(reverse('activity_detail', args=[self.activity.id]))

        self.assertContains(response, "Seleccione un bono:")
        self.assertContains(response, f'{self.bonus1.get_bonus_type_display()} - {self.bonus1.price:.2f}€')
        self.assertContains(response, f'{self.bonus2.get_bonus_type_display()} - {self.bonus2.price:.2f}€')

