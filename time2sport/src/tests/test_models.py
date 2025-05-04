import os
from django.test import TestCase
from src.models import Session, Reservation
from sbai.models import Schedule, SportFacility, Activity, Bonus, DayOfWeek
from sgu.models import User
from slegpn.models import ProductBonus
from datetime import date, datetime, time, timedelta
from django.utils import timezone


class SessionModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):

        # Create the session for the activity schedule
        schedule_activity = Schedule.objects.create(
            day_of_week=DayOfWeek.MARTES,
            hour_begin="08:00:00",
            hour_end="9:00:00"
        )

        # Create the session for the facility schedule
        schedule_facility = Schedule.objects.create(
            day_of_week=DayOfWeek.JUEVES,
            hour_begin="09:00:00",
            hour_end="10:00:00"
        )

        # Create an activity
        activity = Activity.objects.create(
            name="Partido de Futbol",
            location="Campo de Fútbol",
            description="Entrenamiento futbol sala para 5 jugadores",
            activity_type="Terrestre",
        )
        activity.schedules.add(schedule_activity)

        # Create a facility
        facility = SportFacility.objects.create(
            name="Pista de Tenis",
            number_of_facilities=2,
            description="Una pista de tenis bien mantenida.",
            hour_price=30.0,
            facility_type="Exterior",
        )
        facility.schedules.add(schedule_facility)

        cls.session_activity = Session.objects.create(
            activity=activity,
            facility=None,
            schedule=schedule_activity,
            capacity=5,
            free_places=5,
            date=date.today(),
            start_time=time(8, 0),
            end_time=time(9, 0)
        )

        cls.session_facility = Session.objects.create(
            activity=None,
            facility=facility,
            schedule=schedule_facility,
            capacity=2,
            free_places=2,
            date=date.today(),
            start_time=time(9, 0),
            end_time=time(10, 0)
        )

        cls.user = User.objects.create(
            username="ramon",
            email="ramon@example.com",
            password="test1234",
            is_uam=False,
            user_type='notUAM',
        )
        cls.user.has_valid_bono_for_activity = lambda actividad: True

        cls.bonus = Bonus.objects.create(
            activity=cls.session_activity.activity,
            bonus_type='single',
            price=10.0
        )

        cls.product_bonus = ProductBonus.objects.create(
            user=cls.user,
            bonus=cls.bonus,
            one_use_available=True
        )

    def test_session_activity_fields(self):
        """Verifies that the session of an activity fields are correct"""
        session = self.session_activity
        self.assertEqual(session.activity.name, "Partido de Futbol")
        self.assertIsNone(session.facility)
        self.assertEqual(session.schedule.day_of_week, DayOfWeek.MARTES)
        self.assertEqual(session.capacity, 5)
        self.assertEqual(session.free_places, 5)
        self.assertEqual(session.start_time, time(8, 0))
        self.assertEqual(session.end_time, time(9, 0))

    def test_session_facility_fields(self):
        """Verifies that the session of an facility fields are correct"""
        session = self.session_facility
        self.assertIsNone(session.activity)
        self.assertEqual(session.facility.name, "Pista de Tenis")
        self.assertEqual(session.schedule.day_of_week, DayOfWeek.JUEVES)
        self.assertEqual(session.capacity, 2)
        self.assertEqual(session.free_places, 2)
        self.assertEqual(session.start_time, time(9, 0))
        self.assertEqual(session.end_time, time(10, 0))

    def test_session_is_full(self):
        """Verifies that the session is full"""
        session = self.session_activity
        session.free_places = 0
        session.save()
        self.assertTrue(session.is_full())

    def test_session_is_not_full(self):
        """Verifies that the session is not full"""
        session = self.session_activity
        self.assertFalse(session.is_full())

    def test_session_add_reservation_activity(self):
        """Correctly adds a reservation of an activity session"""
        session = self.session_activity
        user = self.user

        reservation = session.add_reservation_activity(user)

        self.assertIsNotNone(reservation)
        self.assertEqual(reservation.user, user)
        self.assertEqual(reservation.session, session)
        session.refresh_from_db()
        self.assertEqual(session.free_places, 4)

    def test_no_reservation_when_session_is_full(self):
        """Verifies that a reservation can't be made when the session is full"""
        session = self.session_activity
        session.free_places = 0
        session.save()

        self.user.has_valid_bono_for_activity = lambda actividad: True
        reservation = session.add_reservation_activity(self.user)

        self.assertIsNone(reservation)

    def test_no_duplicate_reservation(self):
        """Verifies that a reservation can't be made when it has already been reserved"""
        session = self.session_activity
        self.user.has_valid_bono_for_activity = lambda actividad: True

        # First reservation
        session.add_reservation_activity(self.user)

        # Attempt a ducplicate reservation
        reservation = session.add_reservation_activity(self.user)
        self.assertIsNone(reservation)

    def test_single_use_bonus_is_used(self):
        """Verifies that in case the reservation is made with a single use bonus, it expires"""
        session = self.session_activity

        self.user.has_valid_bono_for_activity = lambda actividad: True

        reservation = session.add_reservation_activity(self.user)

        self.product_bonus.refresh_from_db()

        self.assertFalse(self.product_bonus.one_use_available)
        self.assertIsNotNone(reservation)
        self.assertEqual(reservation.user, self.user)
        self.assertEqual(reservation.session, session)

    def test_session_activity_str(self):
        """Checks that the string format of the session activity is correct"""
        s = self.session_activity
        expected = f"{s.activity.name} - {s.date.strftime('%d/%m/%Y')} {s.start_time}-{s.end_time} ({s.free_places}/{s.capacity} disponibles)"
        self.assertEqual(str(s), expected)

    def test_session_facility_str(self):
        """Checks that the string format of the session facility is correct"""
        s = self.session_facility
        expected = f"{s.facility.name} - {s.date.strftime('%d/%m/%Y')} {s.start_time.strftime('%H:%M')}:{s.end_time.strftime('%H:%M')} ({s.free_places}/{s.capacity} disponibles)"
        self.assertEqual(str(s), expected)


class ReservationModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create an activity
        activity = Activity.objects.create(
            name="Partido de Futbol",
            location="Campo de Fútbol",
            description="Entrenamiento futbol sala para 5 jugadores",
            activity_type="Terrestre",
        )
        activity.schedules.add(
            Schedule.objects.create(
                day_of_week=DayOfWeek.MARTES,
                hour_begin="08:00:00",
                hour_end="14:00:00"
            )
        )

        # Create the session for the activity schedule
        schedule_activity = Schedule.objects.create(
            day_of_week=DayOfWeek.MARTES,
            hour_begin="08:00:00",
            hour_end="9:00:00"
        )

        # Create a session
        session = Session.objects.create(
            activity=activity,
            facility=None,
            schedule=schedule_activity,
            capacity=5,
            free_places=5,
            date=date.today(),
            start_time=time(8, 0),
            end_time=time(9, 0)
        )

        # Create a user
        user = User.objects.create(
            username="ramon",
            email="ramon@example.com",
            password="test1234",
            is_uam=False,
            user_type='notUAM',
        )

        # Create a bonus
        bonus = Bonus.objects.create(
            activity=session.activity,
            bonus_type='single',
            price=10.0
        )

        # Create a product bonus
        product_bonus = ProductBonus.objects.create(
            user=user,
            bonus=bonus,
            one_use_available=True
        )

        # Create a reservation
        cls.reservation = Reservation.objects.create(
            user=user,
            session=session,
            bonus=product_bonus
        )

    def test_reservation_fields(self):
        """Checks that the reservation fields are correct"""
        self.assertEqual(self.reservation.user.username, "ramon")
        self.assertEqual(
            self.reservation.session.activity.name, "Partido de Futbol")
        self.assertEqual(self.reservation.bonus.bonus.bonus_type, "single")

    def test_reservation_str(self):
        """Checks that the string representation of a reservation is correct"""
        expected_str = f"{self.reservation.user.username} - {self.reservation.session}"
        self.assertEqual(str(self.reservation), expected_str)

    def test_reservation_cancel_successful(self):
        """Checks that the reservation is succesfully canceled"""
        self.reservation.session.date = date.today() + timedelta(days=1)
        self.reservation.session.start_time = (
            datetime.now() + timedelta(hours=3)).time()
        self.reservation.session.save()

        #Verify that the reservation was correctly cancelled
        was_cancelled = self.reservation.cancel()
        self.assertTrue(was_cancelled)
        self.assertFalse(Reservation.objects.filter(
            id=self.reservation.id).exists())

    def test_reservation_cancel_fails_due_to_time_limit(self):
        """Checks that the reservation can't be cancelled when less that two hours from the start"""
        self.reservation.session.date = date.today()
        self.reservation.session.start_time = (
            datetime.now() + timedelta(minutes=30)).time()
        self.reservation.session.save()

        #Verify that the reservation isn't cancelled because of the time of cancellation
        was_cancelled = self.reservation.cancel()
        self.assertFalse(was_cancelled)
        self.assertTrue(Reservation.objects.filter(
            id=self.reservation.id).exists())
