from django.test import TestCase
from django.utils import timezone
from datetime import timedelta, time
from datetime import datetime
from django.contrib.auth import get_user_model
from django.urls import reverse

from slegpn.models import WaitingList, ProductBonus
from src.models import Session, Reservation
from sbai.models import Activity, Schedule, DayOfWeek, Bonus

User = get_user_model()

class WaitingListTestCase(TestCase):
    def setUp(self):
        # Create users
        self.user1 = User.objects.create_user(username="testuser", password="testpassword")
        self.user2 = User.objects.create_user(username="testuser2", password="testpassword2")

        # Create a schedule
        self.schedule_1 = Schedule.objects.create(
            day_of_week=DayOfWeek.LUNES,
            hour_begin='08:00:00',
            hour_end='09:00:00'
        )
        self.schedule_2 = Schedule.objects.create(
            day_of_week=DayOfWeek.MARTES,
            hour_begin='08:00:00',
            hour_end='09:00:00'
        )

        # Create an activity
        self.activity = Activity.objects.create(
            name="Example Activity",
            description="Example activity for a test"
        )
        self.activity.schedules.add(self.schedule_1)
        self.activity.schedules.add(self.schedule_2)

        # Session with no free places (full)
        self.session_full = Session.objects.create(
            activity=self.activity,
            schedule=self.schedule_1,
            capacity=1,
            free_places=0,
            date=timezone.now().date() + timedelta(days=1),
            start_time=datetime.strptime(self.schedule_1.hour_begin, '%H:%M:%S').time(),
            end_time=datetime.strptime(self.schedule_1.hour_end, '%H:%M:%S').time()
        )

        # Session with available places
        self.session_available = Session.objects.create(
            activity=self.activity,
            schedule=self.schedule_2,
            capacity=1,
            free_places=1,
            date=timezone.now().date() + timedelta(days=1),
            start_time=datetime.strptime(self.schedule_2.hour_begin, '%H:%M:%S').time(),
            end_time=datetime.strptime(self.schedule_2.hour_end, '%H:%M:%S').time()
        )

        # Create a bonus
        self.bonus = Bonus.objects.create(
            activity = self.activity,
            bonus_type = 'semester',
            price = 50.0,
        )
        
        # Add the bonus to the user
        self.product_bonus_1 = ProductBonus.objects.create(
            user=self.user1,
            bonus=self.bonus,
            purchase_date=timezone.now(),
            date_begin=timezone.now().date(),
            date_end=timezone.now().date() + timedelta(days=30)
        )

        # Add the bonus to the user2
        self.product_bonus_2 = ProductBonus.objects.create(
            user=self.user2,
            bonus=self.bonus,
            purchase_date=timezone.now(),
            date_begin=timezone.now().date(),
            date_end=timezone.now().date() + timedelta(days=30)
        )


    def test_add_to_waiting_list_when_full(self):
        """ A user can join the waiting list only if the session is full. """

        # Login user
        self.client.login(username="testuser", password="testpassword")

        # Check if the session is full
        response = self.client.get(reverse('activity_detail', args=[self.activity.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Apuntarse a lista de espera")

        # Add user to waiting list
        response = self.client.post(reverse('join_waiting_list', args=[self.session_full.id]), follow=True)

        # Redirect correctly
        self.assertEqual(response.status_code, 200)

        # Check if the user is in the waiting list
        waiting_list = WaitingList.objects.filter(user=self.user1, session=self.session_full)
        self.assertTrue(waiting_list.exists())


    def test_cannot_add_to_waiting_list_when_space_available(self):
        """ A user cannot be added to waiting list when there are free places. """

        # Login user
        self.client.login(username="testuser", password="testpassword")

        # Check if the session is available
        response = self.client.get(reverse('activity_detail', args=[self.activity.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Reservar")

        # Try to add user to waiting list
        response = self.client.post(reverse('join_waiting_list', args=[self.session_available.id]), follow=True)

        # Check if the user is not in the waiting list
        waiting_list = WaitingList.objects.filter(user=self.user1, session=self.session_available)
        self.assertFalse(waiting_list.exists())


    def test_waiting_list_ordering_by_join_date(self):
        """ Entries in the waiting list are ordered by join_date. """

        # Login first user
        self.client.login(username="testuser", password="testpassword")

        # Add first user to waiting list
        self.client.post(reverse('join_waiting_list', args=[self.session_full.id]), follow=True)

        # Login second user
        self.client.logout()
        self.client.login(username="testuser2", password="testpassword2")

        # Add second user to waiting list
        self.client.post(reverse('join_waiting_list', args=[self.session_full.id]), follow=True)

        # Check if the waiting list is ordered by join_date
        waiting_list = WaitingList.objects.filter(session=self.session_full)
        self.assertEqual(waiting_list.count(), 2)
        self.assertEqual(waiting_list.first().user, self.user1)
        self.assertEqual(waiting_list.last().user, self.user2)


    def test_remove_from_waiting_list(self):
        """ A user can remove themselves from the waiting list. """

        # Login user
        self.client.login(username="testuser", password="testpassword")

        # Add user to waiting list
        self.client.post(reverse('join_waiting_list', args=[self.session_full.id]), follow=True)

        # Check if the user is in the waiting list
        waiting_list = WaitingList.objects.filter(user=self.user1, session=self.session_full)
        self.assertTrue(waiting_list.exists())

        # Remove user from waiting list
        response = self.client.post(reverse('cancel_waiting_list', args=[self.session_full.id]), follow=True)

        # Check if the user is removed from the waiting list
        waiting_list = WaitingList.objects.filter(user=self.user1, session=self.session_full)
        self.assertFalse(waiting_list.exists())
