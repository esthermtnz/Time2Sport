from django.test import TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model

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
        with open("static/images/uam.png", "rb") as image:
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
