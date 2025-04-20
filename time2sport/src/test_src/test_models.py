import os
from django.test import TestCase
from src.models import Session, ReservationStatus, Reservation
from sbai.models import Schedule, SportFacility, Activity, Photo, Bonus, DayOfWeek
from sgu.models import User
from slegpn.models import ProductBonus
from datetime import date, time, timedelta
from django.utils import timezone

class SessionModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create an activity
        activity = Activity.objects.create(
            name = "Partido de Futbol",
            location = "Campo de Fútbol",
            description = "Entrenamiento futbol sala para 5 jugadores",
            activity_type = "Terrestre",
        )
        activity.schedules.add(
            Schedule.objects.create(
                day_of_week = DayOfWeek.Martes.value,
                hour_begin = "08:00:00",
                hour_end = "14:00:00"
            )
        )

        # Create a facility
        facility = SportFacility.objects.create(
            name = "Pista de Tenis",
            number_of_facilities = 2,
            description = "Una pista de tenis bien mantenida.",
            hour_price = 30.0,
            facility_type = "Exterior",
        )
        facility.schedules.add(
            Schedule.objects.create(
                day_of_week = DayOfWeek.Jueves.value,
                hour_begin = "09:00:00",
                hour_end = "14:00:00"
            )
        )

        # Create the session for the activity schedule
        schedule_activity = Schedule.objects.create(
            day_of_week = DayOfWeek.Martes.value,
            hour_begin = "08:00:00",
            hour_end = "9:00:00"
        )

        # Create the session for the facility schedule
        schedule_facility = Schedule.objects.create(
            day_of_week = DayOfWeek.Jueves.value,
            hour_begin = "09:00:00",
            hour_end = "10:00:00"
        )

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
            is_uam = False,
            user_type = 'notUAM',
        )
        cls.user.has_valid_bono_for_activity = lambda actividad: True

    def test_session_activity_fields(self):
        session = self.session_activity
        self.assertEqual(session.activity.name, "Partido de Futbol")
        self.assertIsNone(session.facility)
        self.assertEqual(session.schedule.day_of_week, DayOfWeek.Martes.value)
        self.assertEqual(session.capacity, 5)
        self.assertEqual(session.free_places, 5)
        self.assertEqual(session.start_time, time(8, 0))
        self.assertEqual(session.end_time, time(9, 0))


    def test_session_facility_fields(self):
        session = self.session_facility
        self.assertIsNone(session.activity)
        self.assertEqual(session.facility.name, "Pista de Tenis")
        self.assertEqual(session.schedule.day_of_week, DayOfWeek.Jueves.value)
        self.assertEqual(session.capacity, 2)
        self.assertEqual(session.free_places, 2)
        self.assertEqual(session.start_time, time(9, 0))
        self.assertEqual(session.end_time, time(10, 0))

    def test_session_is_full(self):
        session = self.session_activity
        session.free_places = 0
        session.save()
        self.assertTrue(session.is_full())
        
    def test_session_is_not_full(self):
        session = self.session_activity
        self.assertFalse(session.is_full())

    def test_session_add_reservation_activity(self):
        session = self.session_activity
        user = self.user

        reservation = session.add_reservation_activity(user)

        self.assertIsNotNone(reservation)
        self.assertEqual(reservation.user, user)
        self.assertEqual(reservation.session, session)
        self.assertEqual(reservation.status, ReservationStatus.VALID.value)
        session.refresh_from_db()
        self.assertEqual(session.free_places, 4)

    
    def test_no_reservation_when_session_is_full(self):
        session = self.session_activity
        session.free_places = 0
        session.save()

        self.user.has_valid_bono_for_activity = lambda actividad: True
        reservation = session.add_reservation_activity(self.user)

        self.assertIsNone(reservation)

    def test_no_duplicate_reservation(self):
        session = self.session_activity
        self.user.has_valid_bono_for_activity = lambda actividad: True

        # First reservation
        session.add_reservation_activity(self.user)
        
        # Attempt a ducplicate reservation
        reservation = session.add_reservation_activity(self.user)
        self.assertIsNone(reservation)

    def test_single_use_bonus_is_used(self):
        session = self.session_activity

        # Crea un bono y producto asociado
        bonus = Bonus.objects.create(
            activity=session.activity,
            bonus_type='single',
            price = 10.0
        )

        product_bonus = ProductBonus.objects.create(
            user=self.user,
            bonus=bonus,
            one_use_available=True
        )

        self.user.has_valid_bono_for_activity = lambda actividad: True

        reservation = session.add_reservation_activity(self.user)

        product_bonus.refresh_from_db()

        self.assertFalse(product_bonus.one_use_available)
        self.assertIsNotNone(reservation)
        self.assertEqual(reservation.user, self.user)
        self.assertEqual(reservation.session, session)

    def test_session_activity_str(self):
        s = self.session_activity
        expected = f"{s.activity.name} - {s.date.strftime('%d/%m/%Y')} {s.start_time}-{s.end_time} ({s.free_places}/{s.capacity} disponibles)"
        self.assertEqual(str(s), expected)

    def test_session_facility_str(self):
        s = self.session_facility
        expected = f"{s.facility.name} - {s.date.strftime('%d/%m/%Y')} {s.start_time.strftime('%H:%M')}:{s.end_time.strftime('%H:%M')} ({s.free_places}/{s.capacity} disponibles)"
        self.assertEqual(str(s), expected)

class ReservationModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create an activity
        activity = Activity.objects.create(
            name = "Partido de Futbol",
            location = "Campo de Fútbol",
            description = "Entrenamiento futbol sala para 5 jugadores",
            activity_type = "Terrestre",
        )
        activity.schedules.add(
            Schedule.objects.create(
                day_of_week = DayOfWeek.Martes.value,
                hour_begin = "08:00:00",
                hour_end = "14:00:00"
            )
        )

        # Create the session for the activity schedule
        schedule_activity = Schedule.objects.create(
            day_of_week = DayOfWeek.Martes.value,
            hour_begin = "08:00:00",
            hour_end = "9:00:00"
        )

        #Create a session
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

        #Create a user
        user = User.objects.create(
            username="ramon",
            email="ramon@example.com",
            password="test1234",
            is_uam = False,
            user_type = 'notUAM',
        )

        #Create a reservation
        cls.reservation = Reservation.objects.create(
            user = user,
            session = session,
            status = ReservationStatus.VALID.value
        )

    def test_reservation_fields(self):
        reservation = self.reservation
        self.assertEqual(reservation.user.username, "ramon")
        self.assertEqual(reservation.session.activity.name, "Partido de Futbol")
        self.assertEqual(reservation.status, ReservationStatus.VALID.value)


    def test_reservation_cancel(self):
        reservation = self.reservation
        session = reservation.session
        session.date = (timezone.now() + timedelta(days=1)).date() 
        session.start_time = (timezone.now() + timedelta(hours=3)).time()
        session.save()

        bonus = Bonus.objects.create(
            activity=session.activity,
            bonus_type='single',
            price=10.0
        )

        ProductBonus.objects.create(
            user=reservation.user,      
            bonus=bonus,
            one_use_available=False
        )

        initial_free_places = session.free_places

        result = reservation.cancel()

        self.assertTrue(result)
        self.assertEqual(Session.objects.get(id=session.id).free_places, initial_free_places + 1)
        self.assertFalse(Reservation.objects.filter(id=reservation.id).exists())

        # Checks that the bonus is restored
        product_bonus = ProductBonus.objects.filter(user=reservation.user, bonus=bonus).last()
        self.assertTrue(product_bonus.one_use_available)

    def test_reservation_cancel_fails_due_to_time_limit(self):
        reservation = self.reservation
        session = reservation.session
        session.date = timezone.now().date()
        session.start_time = (timezone.now() + timedelta(minutes=90)).time()
        session.save()

        result = reservation.cancel()

        self.assertFalse(result)
        self.assertTrue(Reservation.objects.filter(id=reservation.id).exists())

    def test_reservation_cancel_fails_due_to_invalid_status(self):
        reservation = self.reservation
        reservation.status = ReservationStatus.CANCELLED.value
        reservation.save()

        result = reservation.cancel()
        self.assertIsNone(result)
        self.assertTrue(Reservation.objects.filter(id=reservation.id).exists())


    def test_reservation_str(self):
        reservation = self.reservation
        expected = f"{reservation.user.username} - {reservation.session} ({reservation.status})"
        self.assertEqual(str(reservation), expected)