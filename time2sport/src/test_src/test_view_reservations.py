from django.test import TestCase
from datetime import datetime, time, date, timedelta
from django.urls import reverse
from src.models import Session, Reservation
from sbai.models import Schedule, SportFacility, Activity, Bonus, DayOfWeek
from sgu.models import User
from slegpn.models import ProductBonus
from src.views import _is_conflict_reserved_sessions, _is_conflict_chosen_sessions, _get_session_split_data


class ReservationsViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):

        # Create the session for the activity schedule
        schedule_activity = Schedule.objects.create(
            day_of_week = DayOfWeek.MARTES,
            hour_begin = "08:00:00",
            hour_end = "9:00:00"
        )

        # Create an activity
        cls.activity = Activity.objects.create(
            name = "Partido de Futbol",
            location = "Campo de Fútbol",
            description = "Entrenamiento futbol sala para 5 jugadores",
            activity_type = "Terrestre",
        )
        cls.activity.schedules.add(schedule_activity)

        #Create a session
        cls.session = Session.objects.create(
            activity=cls.activity,
            facility=None,
            schedule=schedule_activity,
            capacity=5,
            free_places=5,
            date=date.today(),
            start_time=time(8, 0),
            end_time=time(9, 0)
        )

        #Create a session
        cls.session_2 = Session.objects.create(
            activity=cls.activity,
            facility=None,
            schedule=schedule_activity,
            capacity=5,
            free_places=5,
            date=date.today(),
            start_time=time(10, 0),
            end_time=time(11, 0)
        )

        #Create a user
        cls.user = User.objects.create(
            username="ramon",
            email="ramon@example.com",
            password="test1234",
            is_uam = False,
            user_type = 'notUAM',
        )

        #Create a bonus
        bonus = Bonus.objects.create(
            activity=cls.session.activity,
            bonus_type='single',
            price=10.0
        )

        #Create a product bonus
        product_bonus = ProductBonus.objects.create(
            user= cls.user,      
            bonus=bonus,
            one_use_available=True
        )

        #Create a reservation
        cls.reservation = Reservation.objects.create(
            user = cls.user,
            session = cls.session,
            bonus = product_bonus
        )
    
    def test_redirect_for_unauthenticated_users(self):
        "Verifies that the users ared logged in before accessing the template"
        response = self.client.get(reverse('reservations'))
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(response, f"/accounts/login/?next={reverse('reservations')}")

    def test_reservations(self):
        "Checks that the future reservations are correctly displayed"
        self.client.force_login(self.user)

        response = self.client.get(reverse('reservations'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reservations.html')

        self.assertIn('reservations', response.context)
        reservations = response.context['reservations']
        self.assertEqual(response.context['active_tab'], 'future_reservations')

        self.assertEqual(len(reservations), 1)
        self.assertEqual(reservations[0], self.reservation)

        self.assertContains(response, self.activity.name)
        self.assertContains(response, self.reservation.session.date.strftime('%d/%m/%Y'))
        self.assertContains(response, self.reservation.session.end_time.strftime('%H:%M'))
        self.assertContains(response, self.reservation.session.date.strftime('%A'))
        self.assertContains(response, self.activity.location)

        #Check Cancelar button
        self.assertContains(response, 'class="btn btn-danger">Cancelar</a>')

    def test_any_future_reservations(self):
        "Checks that in case there isn't any future reservation a message is shown"
        self.client.force_login(self.user)

        self.session.date = date.today() - timedelta(days=1)
        self.session.save()

        response = self.client.get(reverse('reservations'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No tienes reservas agendadas.")

    def test_past_reservation_not_displayed(self):
        "Checks that in case a past reservations exist, it is not displayed"
        self.client.force_login(self.user)

        self.session.date = date.today() - timedelta(days=3)
        self.session.save()

        response = self.client.get(reverse('reservations'))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.activity.name)

    def test_multiple_future_reservations(self):
        "Checks that in case there are multiple reservations both are displayed"
        self.client.force_login(self.user)

        reservation_2 = Reservation.objects.create(
            user=self.user,
            session=self.session_2,
            bonus=self.reservation.bonus
        )

        response = self.client.get(reverse('reservations'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['reservations']), 2)

        #Session 1
        self.assertContains(response, self.activity.name)
        self.assertContains(response, self.reservation.session.date.strftime('%d/%m/%Y'))
        self.assertContains(response, self.reservation.session.end_time.strftime('%H:%M'))
        self.assertContains(response, self.reservation.session.date.strftime('%A'))
        self.assertContains(response, self.activity.location)

        #Session 2
        self.assertContains(response, self.activity.name)
        self.assertContains(response, reservation_2.session.date.strftime('%d/%m/%Y'))
        self.assertContains(response, reservation_2.session.end_time.strftime('%H:%M'))
        self.assertContains(response, reservation_2.session.date.strftime('%A'))
        self.assertContains(response, self.activity.location)

        #Check Cancelar button
        self.assertContains(response, 'class="btn btn-danger">Cancelar</a>')

    def test_reservations_are_ordered_by_date(self):
        "Checks that the sessions are displayed in the correct order"
        self.client.force_login(self.user)

        future_date = date.today() + timedelta(days=5)
        earlier_date = date.today() + timedelta(days=1)

        self.session.date = future_date
        self.session.save()

        self.session_2.date = earlier_date
        self.session_2.save()

        Reservation.objects.create(
            user=self.user,
            session=self.session_2,
            bonus=self.reservation.bonus
        )

        response = self.client.get(reverse('reservations'))
        dates = [r.session.date for r in response.context['reservations']]
        self.assertEqual(dates, sorted(dates))



class PastReservationsViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        
        # Create the session for the activity schedule
        schedule_activity = Schedule.objects.create(
            day_of_week = DayOfWeek.MARTES,
            hour_begin = "08:00:00",
            hour_end = "9:00:00"
        )

        # Create an activity
        cls.activity = Activity.objects.create(
            name = "Partido de Futbol",
            location = "Campo de Fútbol",
            description = "Entrenamiento futbol sala para 5 jugadores",
            activity_type = "Terrestre",
        )
        cls.activity.schedules.add(schedule_activity)

        #Create a session
        cls.session = Session.objects.create(
            activity=cls.activity,
            facility=None,
            schedule=schedule_activity,
            capacity=5,
            free_places=5,
            date=date.today() - timedelta(days=5),
            start_time=time(8, 0),
            end_time=time(9, 0)
        )

        #Create a session
        cls.session_2 = Session.objects.create(
            activity=cls.activity,
            facility=None,
            schedule=schedule_activity,
            capacity=5,
            free_places=5,
            date=date.today() - timedelta(days=5),
            start_time=time(10, 0),
            end_time=time(11, 0)
        )

        #Create a user
        cls.user = User.objects.create(
            username="ramon",
            email="ramon@example.com",
            password="test1234",
            is_uam = False,
            user_type = 'notUAM',
        )

        #Create a bonus
        bonus = Bonus.objects.create(
            activity=cls.session.activity,
            bonus_type='single',
            price=10.0
        )

        #Create a product bonus
        product_bonus = ProductBonus.objects.create(
            user= cls.user,      
            bonus=bonus,
            one_use_available=True
        )

        #Create a reservation
        cls.reservation = Reservation.objects.create(
            user = cls.user,
            session = cls.session,
            bonus = product_bonus
        )
    
    def test_redirect_for_unauthenticated_users(self):
        "Verifies that the users ared logged in before accessing the template"
        response = self.client.get(reverse('past-reservations'))
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(response, f"/accounts/login/?next={reverse('past-reservations')}")

    def test_past_reservations(self):
        "Checks that the past reservation is correclty displayed in the view"
        self.client.force_login(self.user)

        response = self.client.get(reverse('past-reservations'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'past_reservations.html')

        self.assertIn('past_reservations', response.context)
        past_reservations = response.context['past_reservations']
        self.assertEqual(response.context['active_tab'], 'past_reservations')

        self.assertEqual(len(past_reservations), 1)
        self.assertEqual(past_reservations[0], self.reservation)

        self.assertContains(response, self.activity.name)
        self.assertContains(response, self.reservation.session.date.strftime('%d/%m/%Y'))
        self.assertContains(response, self.reservation.session.end_time.strftime('%H:%M'))
        self.assertContains(response, self.reservation.session.date.strftime('%A'))
        self.assertContains(response, self.activity.location)

    def test_any_past_reservations(self):
        "Checks that in case there isn't any past reservation a message is shown"
        self.client.force_login(self.user)

        self.session.date = date.today() + timedelta(days=1)
        self.session.save()

        response = self.client.get(reverse('past-reservations'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No tienes reservas pasadas.")

    def test_future_reservation_not_displayed(self):
        "Checks that in case there is a future reservation it is not displayed"
        self.client.force_login(self.user)

        self.session.date = date.today() + timedelta(days=2)
        self.session.save()

        response = self.client.get(reverse('past-reservations'))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.activity.name)

    def test_multiple_past_reservations(self):
        "Checks that in case there are multiple past reservation all of them are displayed"
        self.client.force_login(self.user)

        reservation_2 = Reservation.objects.create(
            user=self.user,
            session=self.session_2,
            bonus=self.reservation.bonus
        )

        response = self.client.get(reverse('past-reservations'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['past_reservations']), 2)

        #Session 1
        self.assertContains(response, self.activity.name)
        self.assertContains(response, self.reservation.session.date.strftime('%d/%m/%Y'))
        self.assertContains(response, self.reservation.session.end_time.strftime('%H:%M'))
        self.assertContains(response, self.reservation.session.date.strftime('%A'))
        self.assertContains(response, self.activity.location)

        #Session 2
        self.assertContains(response, self.activity.name)
        self.assertContains(response, reservation_2.session.date.strftime('%d/%m/%Y'))
        self.assertContains(response, reservation_2.session.end_time.strftime('%H:%M'))
        self.assertContains(response, reservation_2.session.date.strftime('%A'))
        self.assertContains(response, self.activity.location)


    def test_reservations_are_ordered_by_date(self):
        "Checks that the reservations are ordered as expected"
        self.client.force_login(self.user)

        earlier_date = date.today() - timedelta(days=1)
        long_past_date = date.today() - timedelta(days=5)

        self.session.date = earlier_date
        self.session.save()

        self.session_2.date = long_past_date
        self.session_2.save()

        Reservation.objects.create(
            user=self.user,
            session=self.session_2,
            bonus=self.reservation.bonus
        )

        response = self.client.get(reverse('past-reservations'))
        dates = [r.session.date for r in response.context['past_reservations']]
        self.assertEqual(dates, sorted(dates, reverse=True))
