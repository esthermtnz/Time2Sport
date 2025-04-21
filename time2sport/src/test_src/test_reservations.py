from django.test import TestCase
from datetime import datetime, time, date, timedelta
from django.urls import reverse
from src.models import Session, Reservation
from sbai.models import Schedule, SportFacility, Activity, Bonus, DayOfWeek
from sgu.models import User
from slegpn.models import ProductBonus, Notification
from src.views import _is_conflict_reserved_sessions, _is_conflict_chosen_sessions, _get_session_split_data


class ReserveActivitySessionViewTest(TestCase):

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
        response = self.client.get(reverse('activity_detail', args=[self.activity.id]))
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(response, f'/accounts/login/?next=/activities/{self.activity.id}/')

    def test_reserve_activity_session(self):
        "Makes a reservation of a session activity successfully"
        self.client.force_login(self.user)

        session_id = self.session_2.id
        self.user.has_valid_bono_for_activity = lambda actividad: True

        response = self.client.get(reverse('reserve_activity_session', args=[session_id]))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('activity_detail', args=[self.activity.id]))

        self.assertTrue(Reservation.objects.filter(user=self.user, session=self.session_2).exists())

        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Reserva realizada con éxito.")

        notification = Notification.objects.filter(user=self.user).last()
        self.assertIsNotNone(notification)
        self.assertIn("Reserva realizada con éxito", notification.title)
        self.assertIn(f"Has realizado una reserva de {self.session_2.activity} para el día {self.session_2.date.strftime('%d/%m/%Y')}.", notification.content)

    def test_conflicting_reservation(self):
        "Attempts to make a reservation that has a schedule conflict with an already made reservation"
        self.client.force_login(self.user)
        self.user.has_valid_bono_for_activity = lambda actividad: True

        response = self.client.get(reverse('reserve_activity_session', args=[self.session.id]))

        self.assertRedirects(response, reverse('activity_detail', args=[self.activity.id]))
        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertIn("Ya tienes una reserva para esa hora", str(messages[0]))

    def test_reservation_fails_when_session_full(self):
        "Attempts to make a reservation when the session is full"
        self.client.force_login(self.user)
        self.user.has_valid_bono_for_activity = lambda actividad: True

        self.session_2.free_places = 0
        self.session_2.save()

        response = self.client.get(reverse('reserve_activity_session', args=[self.session_2.id]))

        self.assertRedirects(response, reverse('activity_detail', args=[self.activity.id]))
        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertIn("Error al realizar la reserva", str(messages[0]))

    def test_reservation_nonexistant_session(self):
        "Attempts to make a reservation of a non existant session"
        self.client.force_login(self.user)
        invalid_id = 9999

        response = self.client.get(reverse('reserve_activity_session', args=[invalid_id]))
        self.assertEqual(response.status_code, 404)

class CheckReserveFacilitySessionViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):

        # Create the session for the activity schedule
        schedule_activity = Schedule.objects.create(
            day_of_week = DayOfWeek.MARTES,
            hour_begin = "08:00:00",
            hour_end = "9:00:00"
        )

        # Create the session for the facility schedule
        schedule_facility = Schedule.objects.create(
            day_of_week = DayOfWeek.JUEVES,
            hour_begin = "09:00:00",
            hour_end = "14:00:00"
        )

        # Create an activity
        cls.activity = Activity.objects.create(
            name = "Partido de Futbol",
            location = "Campo de Fútbol",
            description = "Entrenamiento futbol sala para 5 jugadores",
            activity_type = "Terrestre",
        )
        cls.activity.schedules.add(schedule_activity)

        # Create a facility
        cls.facility = SportFacility.objects.create(
            name = "Pista de Tenis",
            number_of_facilities = 2,
            description = "Una pista de tenis bien mantenida.",
            hour_price = 30.0,
            facility_type = "Exterior",
        )
        cls.facility.schedules.add(schedule_facility)

        #Create a session
        cls.session = Session.objects.create(
            activity=None,
            facility=cls.facility,
            schedule=schedule_facility,
            capacity=2,
            free_places=2,
            date=date.today(),
            start_time=time(9, 0),
            end_time=time(10, 0)
        )

        cls.session_2 = Session.objects.create(
            activity=None,
            facility=cls.facility,
            schedule=schedule_facility,
            capacity=2,
            free_places=2,
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

        #Create a reservation
        cls.reservation = Reservation.objects.create(
            user = cls.user,
            session = cls.session,
            bonus = None
        )

    def test_redirect_for_unauthenticated_users(self):
        "Verifies that the users ared logged in before accessing the template"
        response = self.client.get(reverse('facility_detail', args=[self.facility.id]))
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(response, f'/accounts/login/?next=/facilities/{self.facility.id}/')
    
    def test_check_reserve_facility_session(self):
        "Checks that a valid selected session proceeds to invoice"
        self.client.force_login(self.user)

        # Delete reservation from db
        self.reservation.delete()

        selected = f"{self.facility.id}|09:00|10:00|{date.today().strftime('%B %d %Y')}"
        
        response = self.client.post(reverse('check_reserve_facility_session'), {
            'facility_id': self.facility.id,
            'selected_sessions': f"{selected}"
        })

        self.assertRedirects(response, reverse('invoice_facility', args=[self.facility.id]))
        self.assertEqual(self.client.session['selected_sessions'], [selected])


    def test_check_reserve_facility_multiple_sessions(self):
        "Checks that multiple valid sessions proceed to invoice"
        self.client.force_login(self.user)

        # Delete reservation from db
        self.reservation.delete()

        selected_1 = f"{self.facility.id}|09:00|10:00|{date.today().strftime('%B %d %Y')}"
        selected_2 = f"{self.facility.id}|10:00|11:00|{date.today().strftime('%B %d %Y')}"

        response = self.client.post(reverse('check_reserve_facility_session'), {
            'facility_id': self.facility.id,
            'selected_sessions': f"{selected_1},{selected_2}"
        })

        self.assertRedirects(response, reverse('invoice_facility', args=[self.facility.id]))
        self.assertEqual(self.client.session['selected_sessions'], [selected_1, selected_2])


    def test_no_sessions_selected(self):
        "Checks that an error message is given when no sessions are selected"
        self.client.force_login(self.user)

        response = self.client.post(reverse('check_reserve_facility_session'), {
            'facility_id': self.facility.id,
            'selected_sessions': ''
        })

        self.assertRedirects(response, reverse('facility_detail', args=[self.facility.id]))
        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertIn('No se ha seleccionado ninguna sesión.', str(messages[0]))

    def test_conflict_between_selected_sessions(self):
        "Checks that redirects in case of a schedule conflict"
        self.client.force_login(self.user)

        selected_1 = f"{self.facility.id}|09:00|10:00|{date.today().strftime('%B %d %Y')}"
        selected_2 = f"{self.facility.id}|09:30|10:30|{date.today().strftime('%B %d %Y')}"  # solapa con la anterior

        response = self.client.post(reverse('check_reserve_facility_session'), {
            'facility_id': self.facility.id,
            'selected_sessions': f"{selected_1},{selected_2}"
        })

        self.assertRedirects(response, reverse('facility_detail', args=[self.facility.id]))
        messages = list(response.wsgi_request._messages)
        self.assertIn("Las reservas seleccionadas se solapan.", str(messages[0]))

    def test_conflict_with_existing_user_reservation(self):
        "Checks that redirects in case of attempting making a reservation on a already reserved spot"
        self.client.force_login(self.user)

        selected = f"{self.facility.id}|09:00|10:00|{date.today().strftime('%B %d %Y')}"

        response = self.client.post(reverse('check_reserve_facility_session'), {
            'facility_id': self.facility.id,
            'selected_sessions': selected
        })

        self.assertRedirects(response, reverse('facility_detail', args=[self.facility.id]))
        messages = list(response.wsgi_request._messages)
        self.assertIn("Ya tienes una reserva para esa hora", str(messages[0]))

class ReserveFacilitySessionViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):

        # Create the session for the activity schedule
        schedule_activity = Schedule.objects.create(
            day_of_week = DayOfWeek.MARTES,
            hour_begin = "08:00:00",
            hour_end = "9:00:00"
        )

        # Create the session for the facility schedule
        schedule_facility = Schedule.objects.create(
            day_of_week = DayOfWeek.JUEVES,
            hour_begin = "09:00:00",
            hour_end = "14:00:00"
        )

        # Create an activity
        cls.activity = Activity.objects.create(
            name = "Partido de Futbol",
            location = "Campo de Fútbol",
            description = "Entrenamiento futbol sala para 5 jugadores",
            activity_type = "Terrestre",
        )
        cls.activity.schedules.add(schedule_activity)

        # Create a facility
        cls.facility = SportFacility.objects.create(
            name = "Pista de Tenis",
            number_of_facilities = 2,
            description = "Una pista de tenis bien mantenida.",
            hour_price = 30.0,
            facility_type = "Exterior",
        )
        cls.facility.schedules.add(schedule_facility)

        #Create a session
        cls.session = Session.objects.create(
            activity=None,
            facility=cls.facility,
            schedule=schedule_facility,
            capacity=2,
            free_places=2,
            date=date.today(),
            start_time=time(9, 0),
            end_time=time(10, 0)
        )

        cls.session_2 = Session.objects.create(
            activity=None,
            facility=cls.facility,
            schedule=schedule_facility,
            capacity=2,
            free_places=2,
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

        #Create a reservation
        cls.reservation = Reservation.objects.create(
            user = cls.user,
            session = cls.session,
            bonus = None
        )

    def test_redirect_if_not_authenticated(self):
        selected = f"{self.facility.id}|09:00|10:00|{date.today().strftime('%B %d %Y')}"
        session = self.client.session
        session['selected_sessions'] = [selected]
        session.save()

        self.client.logout()
        response = self.client.get(reverse('payment-facility-success', args=[self.facility.id]))
        self.assertRedirects(response, f'/accounts/login/?next=/payment-facility-success/{self.facility.id}/')

    def test_reserve_facility_session(self):
        "Creates the reservation of the facility"
        self.client.force_login(self.user)

        selected = f"{self.facility.id}|10:00|11:00|{date.today().strftime('%B %d %Y')}"
        session = self.client.session
        session['selected_sessions'] = [selected]
        session.save()

        response = self.client.get(reverse('payment-facility-success', args=[self.facility.id]))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Reservation.objects.filter(user=self.user, session=self.session_2).exists())

        notification = Notification.objects.filter(user=self.user).last()
        self.assertIsNotNone(notification)
        self.assertIn("Reserva realizada correctamente", notification.title)
        self.assertIn(self.session_2.date.strftime('%d/%m/%Y'), notification.content)

        session_2_updated = Session.objects.get(pk=self.session_2.pk)
        self.assertEqual(session_2_updated.free_places, 1)

    def test_reserve_multiple_sessions(self):
        "Creates multiple reservations for the facility"
        self.client.force_login(self.user)

        selected_1 = f"{self.facility.id}|09:00|10:00|{date.today().strftime('%B %d %Y')}"
        selected_2 = f"{self.facility.id}|10:00|11:00|{date.today().strftime('%B %d %Y')}"

        Reservation.objects.filter(user=self.user, session=self.session).delete()  # limpieza

        session = self.client.session
        session['selected_sessions'] = [selected_1, selected_2]
        session.save()

        response = self.client.get(reverse('payment-facility-success', args=[self.facility.id]))

        self.assertEqual(response.status_code, 200)

        self.assertTrue(Reservation.objects.filter(user=self.user, session=self.session).exists())
        self.assertTrue(Reservation.objects.filter(user=self.user, session=self.session_2).exists())

        notification = Notification.objects.filter(user=self.user).last()
        self.assertIn("Reserva realizada correctamente", notification.title)

    def test_reservation_attempt_session_is_full(self):
        "Checks that an error message is received when attempting to make a reservation on a full session"
        self.client.force_login(self.user)

        self.session.free_places = 0
        self.session.save()

        selected = f"{self.facility.id}|09:00|10:00|{date.today().strftime('%B %d %Y')}"
        session = self.client.session
        session['selected_sessions'] = [selected]
        session.save()

        response = self.client.get(reverse('payment-facility-success', args=[self.facility.id]))

        self.assertEqual(Reservation.objects.filter(user=self.user, session=self.session).count(), 1)  # solo la del setUp

        messages = list(response.wsgi_request._messages)
        self.assertTrue(
            any("La hora 09:00 - 10:00 ya está ocupada." in str(message) for message in messages),
            "No se encontró el mensaje de error esperado en messages"
        )