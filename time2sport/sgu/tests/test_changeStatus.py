from django.test import TestCase
from django.contrib.auth import get_user_model

from django.core import mail

from freezegun import freeze_time
from django.utils.timezone import now, timedelta

User = get_user_model()

"""
UAMStatusTestCase class which contains the tests for the UAM status feature
"""
class UAMStatusTestCase(TestCase):
    def setUp(self):
        """ Create a user and log in """
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword",
            is_uam=None,
            user_type="notUAM",
            email="user@gmail.com"
        )
        self.client.login(username="testuser", password="testpassword")

    def test_change_uam_status_valid(self):
        """ Should allow changing the status to UAM with a valid verification code """

        # Choose the UAM option and enter the email
        response = self.client.post("/uam-verification/", {"user_choice": "3", "email_uam": "user@uam.es"})
        self.assertRedirects(response, "/verificar-codigo-uam/")

        # Capture the verification code sent by email
        self.assertEqual(len(mail.outbox), 1)  # Check that an email was sent
        email_body = mail.outbox[0].body
        lineas = email_body.strip().split("\n")
        codigo_enviado = lineas[4].strip()

        # Put the verification code in the form
        response = self.client.post("/verificar-codigo-uam/", {"codigo": codigo_enviado}, follow=True)

        self.assertEqual(response.status_code, 200)

        # Refresh the user from the database
        self.user.refresh_from_db()

        # Verify that the user is now part of the UAM
        self.assertTrue(self.user.is_uam)
        self.assertEqual(self.user.user_type, "professor")


    def test_change_uam_status_invalid_code(self):
        """ Should reject an invalid verification code """

        # Choose the UAM option and enter the email
        response = self.client.post("/uam-verification/", {"user_choice": "3", "email_uam": "user@uam.es"})
        self.assertRedirects(response, "/verificar-codigo-uam/")
        
        # Invalid code
        codigo_erroneo = "TEST_CODE"

        # Put the invalid verification code in the form
        response = self.client.post("/verificar-codigo-uam/", {"codigo": codigo_erroneo}, follow=True)

        self.assertEqual(response.status_code, 200)

        # Verify that the response contains the correct message
        self.assertContains(response, "Código incorrecto")

        # Refresh the user from the database
        self.user.refresh_from_db()

        # Verify that the user is not part of the UAM
        self.assertIsNone(self.user.is_uam)
        self.assertEqual(self.user.user_type, "notUAM")


    def test_change_uam_status_code_expired(self):
        """ Should reject an expired verification code """

        # Use freeze_time to simulate the passage of time
        with freeze_time(now()) as frozen_time:
            # Choose the UAM option and enter the email
            response = self.client.post("/uam-verification/", {"user_choice": "3", "email_uam": "user@uam.es"})
            self.assertRedirects(response, "/verificar-codigo-uam/")

            # Capture the verification code sent by email
            self.assertEqual(len(mail.outbox), 1)  # Check that an email was sent
            email_body = mail.outbox[0].body
            lineas = email_body.strip().split("\n")
            codigo_enviado = lineas[4].strip()
            
            # Simulate that 11 minutes have passed
            frozen_time.tick(delta=timedelta(minutes=11))

            # Put the expired verification code in the form
            response = self.client.post("/verificar-codigo-uam/", {"codigo": codigo_enviado}, follow=True)

            self.assertEqual(response.status_code, 200)

            # Verify that the response contains the correct message
            self.assertContains(response, "El código de verificación ha expirado. Solicita uno nuevo.")

            # Refresh the user from the database
            self.user.refresh_from_db()

            # Verify that the user is not part of the UAM
            self.assertIsNone(self.user.is_uam)
            self.assertEqual(self.user.user_type, "notUAM")


    def test_change_uam_status_previous_code(self):
        """ Should reject the change if the user is sent an email, but does not enter the code. 
        Tries again and enters the previous code rather than the new one """

        # Choose the UAM option and enter the email
        response = self.client.post("/uam-verification/", {"user_choice": "3", "email_uam": "user@uam.es"})
        self.assertRedirects(response, "/verificar-codigo-uam/")
        
        # Capture the verification code sent by email
        self.assertEqual(len(mail.outbox), 1)
        email_body = mail.outbox[0].body
        lineas = email_body.strip().split("\n")
        codigo_enviado = lineas[4].strip()

        # Repeat the process and enter the previous code
        response = self.client.post("/uam-verification/", {"user_choice": "3", "email_uam": "user@uam.es"})
        self.assertRedirects(response, "/verificar-codigo-uam/")

        # Put the previous verification code in the form
        response = self.client.post("/verificar-codigo-uam/", {"codigo": codigo_enviado}, follow=True)

        self.assertEqual(response.status_code, 200)

        # Verify that the response contains the correct message
        self.assertContains(response, "Código incorrecto")

        # Refresh the user from the database
        self.user.refresh_from_db()

        # Verify that the user is not part of the UAM
        self.assertIsNone(self.user.is_uam)
        self.assertEqual(self.user.user_type, "notUAM")

        # If the user tries again with the correct code, the status should change
        self.assertEqual(len(mail.outbox), 2)
        email_body = mail.outbox[1].body
        lineas = email_body.strip().split("\n")
        codigo_enviado = lineas[4].strip()

        response = self.client.post("/verificar-codigo-uam/", {"codigo": codigo_enviado}, follow=True)

        self.assertEqual(response.status_code, 200)

        # Refresh the user from the database
        self.user.refresh_from_db()

        # Verify that the user is now part of the UAM
        self.assertTrue(self.user.is_uam)
        self.assertEqual(self.user.user_type, "professor")


    def test_change_uam_status_already_being_uam(self):
        """ Should reject the change if the user is already part of the UAM """

        # Change the user to UAM
        self.user.is_uam = True
        self.user.save()

        # Try to change the user UAM status
        response = self.client.get("/uam-verification/")

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/home/")
