from django.test import TestCase, override_settings
from django.utils import timezone
from datetime import timedelta, time
from datetime import datetime
from django.contrib.auth import get_user_model
from django.urls import reverse
from freezegun import freeze_time
from django.utils.timezone import now

from slegpn.models import WaitingList, ProductBonus
from src.models import Session, Reservation
from sbai.models import Activity, Schedule, DayOfWeek, Bonus

User = get_user_model()

class WaitingListTestCase(TestCase):
    def setUp(self):
        # Create users
        self.user1 = User.objects.create_user(username="testuser", password="testpassword")
        self.user2 = User.objects.create_user(username="testuser2", password="testpassword2")
        self.user3 = User.objects.create_user(username="testuser3", password="testpassword3")
        self.user4 = User.objects.create_user(username="testuser4", password="testpassword4")

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

        # Add the bonus to the user3
        self.product_bonus_3 = ProductBonus.objects.create(
            user=self.user3,
            bonus=self.bonus,
            purchase_date=timezone.now(),
            date_begin=timezone.now().date(),
            date_end=timezone.now().date() + timedelta(days=30)
        )

        # Add the bonus to the user4
        self.product_bonus_4 = ProductBonus.objects.create(
            user=self.user4,
            bonus=self.bonus,
            purchase_date=timezone.now(),
            date_begin=timezone.now().date(),
            date_end=timezone.now().date() + timedelta(days=30)
        )


    def test_notify_next_user_when_place_freed(self):
        """ When a new free place appears due to a cancelation, the first user in the list should be notified. """

        # Login first user
        self.client.login(username="testuser", password="testpassword")
        # Reserve session
        self.client.post(reverse('reserve_activity_session', args=[self.session_available.id]), follow=True)

        # Session is completed

        # Login second user
        self.client.login(username="testuser2", password="testpassword2")
        # Add user to waiting list
        self.client.post(reverse('join_waiting_list', args=[self.session_available.id]), follow=True)

        # Login third user
        self.client.login(username="testuser3", password="testpassword3")
        # Add user to waiting list
        self.client.post(reverse('join_waiting_list', args=[self.session_available.id]), follow=True)

        # First user cancels reservation and frees a place
        self.client.logout()
        self.client.login(username="testuser", password="testpassword")
        reservation = Reservation.objects.get(user=self.user1, session=self.session_available)
        self.client.post(reverse('cancel_reservation', args=[reservation.id]), follow=True)

        # Check if the first user in the waiting list is notified
        waiting_list = WaitingList.objects.filter(session=self.session_available)
        self.assertEqual(waiting_list.count(), 2)
        self.assertEqual(waiting_list.first().user, self.user2)

        self.client.logout()
        self.client.login(username="testuser2", password="testpassword2")

        # Check if the notification is received
        self.notification = self.client.get(reverse('notifications'))
        self.assertEqual(self.notification.status_code, 200)
        self.assertContains(self.notification, "¡Apúntate a la sesión, se ha liberado una plaza!")

        # Check if the other user has not received the notification
        self.client.logout()
        self.client.login(username="testuser3", password="testpassword3")
        self.notification = self.client.get(reverse('notifications'))
        self.assertEqual(self.notification.status_code, 200)
        self.assertNotContains(self.notification, "¡Apúntate a la sesión, se ha liberado una plaza!")

    # @override_settings(WAITING_LIST_NOTIFICATION_MINS=1)
    def test_notify_second_place_if_first_cannot(self):
        """ Next user in the waiting list should be notified if the first one cannot reserve. """

        # Login first user
        self.client.login(username="testuser", password="testpassword")
        # Reserve session
        self.client.post(reverse('reserve_activity_session', args=[self.session_available.id]), follow=True)

        # Session is completed

        # Login second user
        self.client.login(username="testuser2", password="testpassword2")
        # Add user to waiting list
        self.client.post(reverse('join_waiting_list', args=[self.session_available.id]), follow=True)

        # Login third user
        self.client.login(username="testuser3", password="testpassword3")
        # Add user to waiting list
        self.client.post(reverse('join_waiting_list', args=[self.session_available.id]), follow=True)

        # First user cancels reservation and frees a place
        self.client.logout()
        self.client.login(username="testuser", password="testpassword")
        reservation = Reservation.objects.get(user=self.user1, session=self.session_available)
        self.client.post(reverse('cancel_reservation', args=[reservation.id]), follow=True)

        # Check if the first user in the waiting list is notified
        waiting_list = WaitingList.objects.filter(session=self.session_available)
        self.assertEqual(waiting_list.count(), 2)
        self.assertEqual(waiting_list.first().user, self.user2)

        self.client.logout()
        self.client.login(username="testuser2", password="testpassword2")

        # Check if the notification is received
        self.notification = self.client.get(reverse('notifications'))
        self.assertEqual(self.notification.status_code, 200)
        self.assertContains(self.notification, "¡Apúntate a la sesión, se ha liberado una plaza!")

        # Check if the other user has not received the notification
        self.client.logout()
        self.client.login(username="testuser3", password="testpassword3")
        self.notification = self.client.get(reverse('notifications'))
        self.assertEqual(self.notification.status_code, 200)
        self.assertNotContains(self.notification, "¡Apúntate a la sesión, se ha liberado una plaza!")

        import time
        # Time passes
        time.sleep(150)

        print(WaitingList.objects.all())

        # Check user is notified
        self.notification = self.client.get(reverse('notifications'))
        self.assertEqual(self.notification.status_code, 200)
        self.assertContains(self.notification, "¡Apúntate a la sesión, se ha liberado una plaza!")



