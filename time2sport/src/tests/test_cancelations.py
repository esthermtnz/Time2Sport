from django.test import TestCase
from datetime import datetime, time, date, timedelta
from django.urls import reverse
from src.models import Session, Reservation
from sbai.models import Schedule, Activity, Bonus, DayOfWeek
from sgu.models import User
from slegpn.models import ProductBonus, Notification
from src.views import _is_conflict_reserved_sessions, _is_conflict_chosen_sessions, _get_session_split_data


class CancelReservationViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Create the session for the activity schedule
        schedule_activity = Schedule.objects.create(
            day_of_week=DayOfWeek.MARTES,
            hour_begin="08:00:00",
            hour_end="9:00:00"
        )
        # Create an activity
        cls.activity = Activity.objects.create(
            name="Partido de Futbol",
            location="Campo de Fútbol",
            description="Entrenamiento futbol sala para 5 jugadores",
            activity_type="Terrestre",
        )
        cls.activity.schedules.add(schedule_activity)

        # Create a session
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

        # Create a user
        cls.user = User.objects.create(
            username="ramon",
            email="ramon@example.com",
            password="test1234",
            is_uam=False,
            user_type='notUAM',
        )

        # Create a bonus
        bonus = Bonus.objects.create(
            activity=cls.session.activity,
            bonus_type='single',
            price=10.0
        )

        # Create a product bonus
        product_bonus = ProductBonus.objects.create(
            user=cls.user,
            bonus=bonus,
            one_use_available=True
        )

        # Create a reservation
        cls.reservation = Reservation.objects.create(
            user=cls.user,
            session=cls.session,
            bonus=product_bonus
        )

    def test_redirect_for_unauthenticated_users(self):
        "Verifies that the users ared logged in before accessing the template"
        response = self.client.get(
            reverse('activity_detail', args=[self.activity.id]))
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(
            response, f'/accounts/login/?next=/activities/{self.activity.id}/')

    def test_cancel_reservation(self):
        "Successfully cancels a reservation"
        self.client.force_login(self.user)

        # Session in the next 3 hours
        now = datetime.now()
        session_datetime = now + timedelta(hours=3)

        self.reservation.session.date = session_datetime.date()
        self.reservation.session.start_time = session_datetime.time()
        self.reservation.session.save()

        response = self.client.get(
            reverse('cancel_reservation', args=[self.reservation.id]))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('reservations'))

        exists = Reservation.objects.filter(id=self.reservation.id).exists()
        self.assertFalse(exists)

        # Check that the error message is showed
        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Reserva cancelada con éxito.")

        notification = Notification.objects.filter(user=self.user).last()
        self.assertIsNotNone(notification)
        self.assertIn("Reserva cancelada con éxito", notification.title)
        self.assertIn(
            f"Has cancelado tu reserva de {self.session.activity.name} correctamente.", notification.content)

    def test_cancel_reservation_less_than_two_hours(self):
        "Attempts to cancel a reservation with less than two hours before the start"
        self.client.force_login(self.user)

        now = datetime.now()
        session_datetime = now + timedelta(hours=1)

        self.reservation.session.date = session_datetime.date()
        self.reservation.session.start_time = session_datetime.time()
        self.reservation.session.save()

        response = self.client.get(
            reverse('cancel_reservation', args=[self.reservation.id]))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('reservations'))

        exists = Reservation.objects.filter(id=self.reservation.id).exists()
        self.assertTrue(exists)

        # Check that the error message is showed
        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(
            messages[0]), "No puedes cancelar una reserva con menos de 2 horas de antelación.")

    def test_cancel_reservation_exactly_two_hours(self):
        "Attempts to cancel a reservation just in time, two hours before the class"
        self.client.force_login(self.user)

        now = datetime.now()
        session_datetime = now + timedelta(hours=2, seconds=1)

        self.reservation.session.date = session_datetime.date()
        self.reservation.session.start_time = session_datetime.time()
        self.reservation.session.save()

        response = self.client.get(
            reverse('cancel_reservation', args=[self.reservation.id]))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('reservations'))

        exists = Reservation.objects.filter(id=self.reservation.id).exists()
        self.assertFalse(exists)

        # Check that the error message is showed
        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Reserva cancelada con éxito.")

        notification = Notification.objects.filter(user=self.user).last()
        self.assertIsNotNone(notification)
        self.assertIn("Reserva cancelada con éxito", notification.title)
        self.assertIn(
            f"Has cancelado tu reserva de {self.session.activity.name} correctamente.", notification.content)

    def test_cancel_nonexistent_reservation(self):
        "Attempts to cancel a non existent reservation"
        self.client.force_login(self.user)
        response = self.client.get(reverse('cancel_reservation', args=[9999]))
        self.assertEqual(response.status_code, 404)

    def test_cannot_cancel_reservation_of_another_user(self):
        "Attempts to cancel the reservation of another user"
        evil_user = User.objects.create(
            username="ana",
            email="ana@example.com",
            password="test3456"
        )
        self.client.force_login(evil_user)

        response = self.client.get(
            reverse('cancel_reservation', args=[self.reservation.id]))
        self.assertEqual(response.status_code, 404)
