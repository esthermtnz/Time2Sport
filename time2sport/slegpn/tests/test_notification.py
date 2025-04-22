from django.test import TestCase
from django.contrib.auth import get_user_model
from slegpn.models import Notification
from django.urls import reverse

User = get_user_model()

class NotificationTestCase(TestCase):
    def test_read_notification(self):
        """ Test that a notification can be marked as read. """
        # Create a user and login
        user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.login(username="testuser", password="testpassword")

        # Create a notification
        notification = Notification.objects.create(
            user=user,
            title="Test notification",
            content="This is a test notification.",
            read=False
        )

        # Mark the notification as read
        response = self.client.post(reverse('mark_as_read', args=[notification.id]), follow=True)

        # Check if the notification is marked as read
        notification.refresh_from_db()
        self.assertTrue(notification.read)

    def test_count_unread_notifications(self):
        """ Test that the count of unread notifications is correct. """
        # Create a user and login
        user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.login(username="testuser", password="testpassword")

        # Create notification
        Notification.objects.create(user=user, title="Test notification 1", content="This is a test notification.", read=False)

        # Count unread notifications
        response = self.client.get(reverse('unread_notifications_count'))

        # Check if the count is correct
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['unread_count'], 1)

        # Create another notification
        notification_2 = Notification.objects.create(user=user, title="Test notification 2", content="This is another test notification.", read=False)

        # Count unread notifications
        response = self.client.get(reverse('unread_notifications_count'))

        # Check if the count is correct
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['unread_count'], 2)

        # Read one notification
        self.client.post(reverse('mark_as_read', args=[notification_2.id]), follow=True)
        
        # Check if the count is correct
        response = self.client.get(reverse('unread_notifications_count'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['unread_count'], 1)
        
