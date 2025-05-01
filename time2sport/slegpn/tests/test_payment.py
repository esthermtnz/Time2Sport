from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta, time
from datetime import datetime
from django.contrib.auth import get_user_model
from unittest.mock import patch

from slegpn.models import WaitingList, ProductBonus, Notification
from src.models import Session, Reservation
from sbai.models import Activity, Schedule, DayOfWeek, Bonus, SportFacility

User = get_user_model()

class TestPaymentWithNotification(TestCase):
    def setUp(self):
        # Create user
        self.user1 = User.objects.create_user(username="testuser", password="testpassword")

        # Create a schedule
        self.schedule_1 = Schedule.objects.create(
            day_of_week=DayOfWeek.LUNES,
            hour_begin='08:00:00',
            hour_end='09:00:00'
        )

        # Create an activity
        self.activity = Activity.objects.create(
            name="Example Activity",
            description="Example activity for a test"
        )
        self.activity.schedules.add(self.schedule_1)

        # Create a session for the activity
        self.session = Session.objects.create(
            activity=self.activity,
            schedule=self.schedule_1,
            capacity=10,
            free_places=10,
            date=timezone.now().date() + timedelta(days=1),
            start_time=datetime.strptime(self.schedule_1.hour_begin, '%H:%M:%S').time(),
            end_time=datetime.strptime(self.schedule_1.hour_end, '%H:%M:%S').time()
        )

        # Create a facility
        self.facility = SportFacility.objects.create(
            name="Example Facility",
            description="Example facility for a test",
            number_of_facilities=1, 
            hour_price=10.0, 
            facility_type='Exterior'
        )
        self.facility.schedules.add(self.schedule_1)
        
        # Create a session for the facility
        self.session_facility = Session.objects.create(
            facility=self.facility,
            schedule=self.schedule_1,
            capacity=1,
            free_places=1,
            date=timezone.now().date() + timedelta(days=1),
            start_time=datetime.strptime(self.schedule_1.hour_begin, '%H:%M:%S').time(),
            end_time=datetime.strptime(self.schedule_1.hour_end, '%H:%M:%S').time()
        )

        # Create a bonus
        self.bonus = Bonus.objects.create(
            activity = self.activity,
            bonus_type = 'semester',
            price = 50.0,
        )

    def test_user_cannot_see_payment_pages_if_not_logged_in(self):
        """ Test that a user cannot see payment pages if not logged in. """

        # Try to access the invoice page for activity without logging in
        response = self.client.get(reverse('invoice_activity', args=[self.activity.id]))
        # Check if the user is redirected to the login page
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"/accounts/login/?next={reverse('invoice_activity', args=[self.activity.id])}")

        # Try to access the invoice page for facility without logging in
        response = self.client.get(reverse('invoice_facility', args=[self.facility.id]))
        # Check if the user is redirected to the login page
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"/accounts/login/?next={reverse('invoice_facility', args=[self.facility.id])}")

        # Try to access the payment success page for activity without logging in
        response = self.client.get(reverse('payment-activity-success', args=[self.activity.id]))
        # Check if the user is redirected to the login page
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"/accounts/login/?next={reverse('payment-activity-success', args=[self.activity.id])}")
        
        # Try to access the payment failed page for activity without logging in
        response = self.client.get(reverse('payment-activity-failed', args=[self.activity.id]))
        # Check if the user is redirected to the login page
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"/accounts/login/?next={reverse('payment-activity-failed', args=[self.activity.id])}")
        
        # Try to access the payment success page for facility without logging in
        response = self.client.get(reverse('payment-facility-success', args=[self.facility.id]))
        # Check if the user is redirected to the login page
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"/accounts/login/?next={reverse('payment-facility-success', args=[self.facility.id])}")
        
        # Try to access the payment failed page for facility without logging in
        response = self.client.get(reverse('payment-facility-failed', args=[self.facility.id]))
        # Check if the user is redirected to the login page
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"/accounts/login/?next={reverse('payment-facility-failed', args=[self.facility.id])}")


    def test_purchase_bonus(self):
        """ Chech that a product bonus is created when a user buys a bonus """

        # Login
        self.client.login(username="testuser", password="testpassword")

        # Go to the activity detail page
        response = self.client.post(reverse('activity_detail', args=[self.activity.id]))

        # Check the bonus appears in the page
        self.assertContains(response, f"{self.bonus.get_bonus_type_display()} - {self.bonus.price}")

        # Buy the bonus
        response = self.client.post(reverse('invoice_activity', args=[self.activity.id]), {
            'bonus_id': self.bonus.id
        })

        # Check invoice page
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Factura")
        self.assertContains(response, self.bonus.get_bonus_type_display())
        self.assertContains(response, self.bonus.price)

        # Check there is a form to pay with PayPal
        self.assertContains(response, '<form action="https://www.sandbox.paypal.com/cgi-bin/webscr"')

        # Assume bonus is correctly paid
        response = self.client.post(reverse('complete_enrollment', args=[self.bonus.id]), follow=True)

        self.assertContains(response, "Pago realizado")
        self.assertContains(response, self.bonus.price)

        # Check that the product bonus was created
        product_bonus = ProductBonus.objects.filter(user=self.user1, bonus=self.bonus).exists()
        self.assertTrue(product_bonus)

        # Check that the notification was created
        notification = Notification.objects.filter(user=self.user1, title="Pago realizado correctamente").exists()
        self.assertTrue(notification)

    def test_purchase_bonus_uam_discount(self):
        """ Check that a product bonus is created when a user buys a bonus and is a UAM member which has a discount """
        
        self.user1.is_uam = True
        self.user1.save()

        # Login
        self.client.login(username="testuser", password="testpassword")

        # Go to the activity detail page
        response = self.client.post(reverse('activity_detail', args=[self.activity.id]))

        # Check the bonus appears in the page
        self.assertContains(response, f"{self.bonus.get_bonus_type_display()} - {self.bonus.price}")

        # Buy the bonus
        response = self.client.post(reverse('invoice_activity', args=[self.activity.id]), {
            'bonus_id': self.bonus.id
        })

        # Check invoice page
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Factura")
        self.assertContains(response, self.bonus.get_bonus_type_display())
        self.assertContains(response, self.bonus.price)
        
        # Check the discount is applied
        total = self.bonus.price * 0.9
        self.assertContains(response, total)
        self.assertContains(response, "Descuento UAM")

        # Check there is a form to pay with PayPal
        self.assertContains(response, '<form action="https://www.sandbox.paypal.com/cgi-bin/webscr"')

        # Assume bonus is correctly paid
        response = self.client.post(reverse('complete_enrollment', args=[self.bonus.id]), follow=True)

        self.assertContains(response, "Pago realizado")

        # Check that the product bonus was created
        product_bonus = ProductBonus.objects.filter(user=self.user1, bonus=self.bonus).exists()
        self.assertTrue(product_bonus)

        # Check that the notification was created
        notification = Notification.objects.filter(user=self.user1, title="Pago realizado correctamente").exists()
        self.assertTrue(notification)
        


    def test_purchase_bonus_failed(self):
        """ Check that a product bonus is not created when the payment fails """
        # Login
        self.client.login(username="testuser", password="testpassword")

        # Go to the activity detail page
        response = self.client.post(reverse('activity_detail', args=[self.activity.id]))

        # Check the bonus appears in the page
        self.assertContains(response, f"{self.bonus.get_bonus_type_display()} - {self.bonus.price}")

        # Buy the bonus
        response = self.client.post(reverse('invoice_activity', args=[self.activity.id]), {
            'bonus_id': self.bonus.id
        })

        # Check invoice page
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Factura")
        self.assertContains(response, self.bonus.get_bonus_type_display())
        self.assertContains(response, self.bonus.price)

        # Check there is a form to pay with PayPal
        self.assertContains(response, '<form action="https://www.sandbox.paypal.com/cgi-bin/webscr"')

        # Assume bonus is not paid correctly
        response = self.client.post(reverse('payment-activity-failed', args=[self.bonus.id]), follow=True)

        self.assertContains(response, "Pago cancelado")
        self.assertContains(response, self.bonus.price)

        # Check that the product bonus was not created
        product_bonus = ProductBonus.objects.filter(user=self.user1, bonus=self.bonus).exists()
        self.assertFalse(product_bonus)

        # Check that the notification was not created
        notification = Notification.objects.filter(user=self.user1, title="Pago realizado correctamente").exists()
        self.assertFalse(notification)

    def test_reserve_facility_session(self):
        """ Check that a reservation is created when a user reserves and pays a facility session """

        # Login
        self.client.login(username="testuser", password="testpassword")

        # Reserve the session
        session = self.client.session
        date = self.session_facility.date.strftime('%B %d %Y')
        begin = self.session_facility.start_time.strftime('%H:%M')
        end = self.session_facility.end_time.strftime('%H:%M')

        session['selected_sessions'] = [
            f"{self.facility.id}|{begin}|{end}|{date}"
        ]
        session.save()
        response = self.client.post(reverse('invoice_facility', args=[self.facility.id]))

        # Check invoice page
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Factura")
        self.assertContains(response, self.facility.name)
        self.assertContains(response, self.facility.hour_price)

        # Check there is a form to pay with PayPal
        self.assertContains(response, '<form action="https://www.sandbox.paypal.com/cgi-bin/webscr"')

        # Assume session is correctly paid
        response = self.client.post(reverse('payment-facility-success', args=[self.facility.id]), follow=True)

        self.assertContains(response, "Pago realizado")
        self.assertContains(response, f"Alquiler {self.facility.name}")

        # Check that the reservation was created
        reservation = Reservation.objects.filter(user=self.user1, session=self.session_facility).exists()
        self.assertTrue(reservation)

        # Check that the notification was created
        notification = Notification.objects.filter(user=self.user1, title="Reserva realizada correctamente").exists()
        self.assertTrue(notification)


    def test_reserve_facility_session_uam_discount(self):
        """ Check that a reservation is created when a user reserves and pays a facility session when being a UAM member which has a discount """

        self.user1.is_uam = True
        self.user1.save()

        # Login
        self.client.login(username="testuser", password="testpassword")

        # Reserve the session
        session = self.client.session
        date = self.session_facility.date.strftime('%B %d %Y')
        begin = self.session_facility.start_time.strftime('%H:%M')
        end = self.session_facility.end_time.strftime('%H:%M')

        session['selected_sessions'] = [
            f"{self.facility.id}|{begin}|{end}|{date}"
        ]
        session.save()
        response = self.client.post(reverse('invoice_facility', args=[self.facility.id]))

        # Check invoice page
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Factura")
        self.assertContains(response, self.facility.name)
        self.assertContains(response, self.facility.hour_price)
        
        # Check the discount is applied 
        total = self.facility.hour_price * 0.9  # Reservation is only made for an hour
        self.assertContains(response, total)
        self.assertContains(response, "Descuento UAM")


        # Check there is a form to pay with PayPal
        self.assertContains(response, '<form action="https://www.sandbox.paypal.com/cgi-bin/webscr"')

        # Assume session is correctly paid
        response = self.client.post(reverse('payment-facility-success', args=[self.facility.id]), follow=True)

        self.assertContains(response, "Pago realizado")
        self.assertContains(response, f"Alquiler {self.facility.name}")

        # Check that the reservation was created
        reservation = Reservation.objects.filter(user=self.user1, session=self.session_facility).exists()
        self.assertTrue(reservation)

        # Check that the notification was created
        notification = Notification.objects.filter(user=self.user1, title="Reserva realizada correctamente").exists()
        self.assertTrue(notification)


    def test_reserve_facility_session_failed(self):
        """ Check that a reservation is not created when the payment fails """
        
        # Login
        self.client.login(username="testuser", password="testpassword")

        # Reserve the session
        session = self.client.session
        date = self.session_facility.date.strftime('%B %d %Y')
        begin = self.session_facility.start_time.strftime('%H:%M')
        end = self.session_facility.end_time.strftime('%H:%M')

        session['selected_sessions'] = [
            f"{self.facility.id}|{begin}|{end}|{date}"
        ]
        session.save()
        response = self.client.post(reverse('invoice_facility', args=[self.facility.id]))

        # Check invoice page
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Factura")
        self.assertContains(response, self.facility.name)
        self.assertContains(response, self.facility.hour_price)

        # Check there is a form to pay with PayPal
        self.assertContains(response, '<form action="https://www.sandbox.paypal.com/cgi-bin/webscr"')

        # Assume session is not paid correctly
        response = self.client.post(reverse('payment-facility-failed', args=[self.facility.id]), follow=True)

        self.assertContains(response, "Pago cancelado")
        self.assertContains(response, f"Alquiler {self.facility.name}")

        # Check that the reservation was not created
        reservation = Reservation.objects.filter(user=self.user1, session=self.session_facility).exists()
        self.assertFalse(reservation)

        # Check that the notification was not created
        notification = Notification.objects.filter(user=self.user1, title="Reserva realizada correctamente").exists()
        self.assertFalse(notification)

