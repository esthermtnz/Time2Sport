from django.test import TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model

from django.core import mail

from freezegun import freeze_time
from django.utils.timezone import now, timedelta

from django.conf import settings
import shutil
import tempfile

User = get_user_model()

"""
ProfilePictureTestCase class which contains the tests for the profile picture feature
"""
@override_settings(MEDIA_ROOT=tempfile.mkdtemp()) # Create a temporary media directory
class ProfilePictureTestCase(TestCase):
    def setUp(self):
        """ Create a user and log in """
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.login(username="testuser", password="testpassword")

    def tearDown(self):
        """ Delete the temporary media directory """
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

    def test_update_profile_picture(self):
        """ It should allow the user to upload a new profile picture and save it """

        # Save the current profile picture
        old_image = self.user.profile.name

        # Use UAM logo as a test image
        with open("gestion_deportiva/static/gestion_deportiva/images/uam.png", "rb") as image:
            image = SimpleUploadedFile("uam_logo.png", image.read(), content_type="image/png")

        # Upload the new image
        response = self.client.post("/edit-profile/", {"profile_image": image}, format="multipart")
        
        # Refresh the user from the database
        self.user.refresh_from_db()
        
        # Verify that the profile picture has changed
        self.assertNotEqual(self.user.profile.name, old_image)

        # Verify that the response is correct
        self.assertRedirects(response, "/profile/")

    def test_upload_invalid_file(self):
        """ It should not allow the user to upload a file that is not an image """

        # Save the current profile picture
        old_image = self.user.profile.name

        # Try to upload an invalid file
        invalid_file = SimpleUploadedFile("test_file.txt", b"invalid_file_content", content_type="text/plain")

        response = self.client.post("/edit-profile/", {"profile_image": invalid_file}, format="multipart")

        # Refresh the user from the database
        self.user.refresh_from_db()

        # Verify that the profile picture has not changed
        self.assertEqual(self.user.profile.name, old_image)

        # Verify that the response is correct
        self.assertRedirects(response, "/profile/")

    def test_profile_picture_not_changed(self):
        """ Profile picture should not change if the user does not select a new one """
        # Save the current profile picture
        original_image = self.user.profile.name

        # Send a request without a file
        response = self.client.post("/profile/", {})

        # Refresh the user from the database
        self.user.refresh_from_db()

        # Verify that the profile picture has not changed
        self.assertEqual(self.user.profile.name, original_image)

        # Verify that the response is correct
        self.assertEqual(response.status_code, 200)


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
            self.assertEqual(len(mail.outbox), 1)
            email_body = mail.outbox[0].body
            lineas = email_body.strip().split("\n")
            codigo_enviado = lineas[4].strip()
            
            # Simulate that 11 minutes have passed
            frozen_time.tick(delta=timedelta(minutes=11))

            # Put the expired verification code in the form
            response = self.client.post("/verificar-codigo-uam/", {"codigo": codigo_enviado}, follow=True)

            self.assertEqual(response.status_code, 200)

            # Verify that the response contains the correct message
            self.assertContains(response, "El código de verificación ha expirado. Solicita uno nuevo.")  # Ajusta según el mensaje en tu app

            # Refresh the user from the database
            self.user.refresh_from_db()

            # Verify that the user is not part of the UAM
            self.assertIsNone(self.user.is_uam)
            self.assertEqual(self.user.user_type, "notUAM")
