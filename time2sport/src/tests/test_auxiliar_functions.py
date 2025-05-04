from django.test import TestCase
from datetime import datetime, time, date
from src.models import Session, Reservation
from sbai.models import Schedule, SportFacility, Activity, Bonus, DayOfWeek
from sgu.models import User
from slegpn.models import ProductBonus
from src.views import _is_conflict_reserved_sessions, _is_conflict_chosen_sessions, _get_session_split_data


class AuxiliarReservationFunctionsView(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Create the session for the activity schedule
        schedule_activity = Schedule.objects.create(
            day_of_week=DayOfWeek.MARTES,
            hour_begin="08:00:00",
            hour_end="9:00:00"
        )

        # Create an activity
        activity = Activity.objects.create(
            name="Partido de Futbol",
            location="Campo de Fútbol",
            description="Entrenamiento futbol sala para 5 jugadores",
            activity_type="Terrestre",
        )
        activity.schedules.add(schedule_activity)

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

    def test_is_conflict_reserved_sessions(self):
        "Confirms that there is a conflict between two reserved sessions"
        input_users_sessions = [self.reservation]
        requested_start = time(8, 30)
        requested_end = time(9, 30)

        result = _is_conflict_reserved_sessions(
            input_users_sessions, requested_start, requested_end)
        self.assertTrue(result)

    def test_no_conflict_reserved_sessions(self):
        "Confirms that there is no conflict between two reserved sessions"
        input_users_sessions = []
        requested_start = time(9, 0)
        requested_end = time(10, 0)

        result = _is_conflict_reserved_sessions(
            input_users_sessions, requested_start, requested_end)
        self.assertFalse(result)

    def test_is_conflict_chosen_sessions(self):
        "Confirms that there is a conflict between two sessions"
        selected_sessions = [
            "1|09:00|10:00|April 21 2025",
            "1|09:30|10:30|April 21 2025"
        ]

        result = _is_conflict_chosen_sessions(selected_sessions)
        self.assertTrue(result)

    def test_no_conflict_chosen_sessions(self):
        "Confirms that there is no conflict between two sessions"
        selected_sessions = [
            "1|09:00|10:00|April 21 2025",
            "1|10:00|11:00|April 21 2025"
        ]

        result = _is_conflict_chosen_sessions(selected_sessions)
        self.assertFalse(result)

    def test_get_session_split_data(self):
        "Checks that the data is correctly splitted"
        input_string = "1|09:00|10:00|April 21 2025"
        facility_id, day, start, end = _get_session_split_data(input_string)
        self.assertEqual(facility_id, "1")
        self.assertEqual(start, time(9, 0))
        self.assertEqual(end, time(10, 0))
        self.assertEqual(day, datetime(2025, 4, 21))
