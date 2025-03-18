from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model

User = get_user_model()

"""
ProfilePictureTestCase class which contains the tests for the profile picture feature
"""
class ProfilePictureTestCase(TestCase):
        def setUp(self):
                # Create a user and log in
                self.user = User.objects.create_user(username="testuser", password="testpassword")
                self.client.login(username="testuser", password="testpassword")

        def test_update_profile_picture(self):
                """ It should allow the user to upload a new profile picture and save it """

                # Create a new image
                image = SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")
                
                # Upload the image
                self.user.profile = image
                # Save the user
                self.user.save()

                # Refresh the user from the database
                self.user.refresh_from_db()

                # Verify that the profile picture has been updated
                self.assertTrue(self.user.profile.name.startswith("users/"))

        def test_upload_invalid_file(self):
                """ It should not allow the user to upload a file that is not an image """

                # Save the current profile picture
                old_image = self.user.profile.name

                # Try to upload an invalid file
                invalid_file = SimpleUploadedFile("test_file.txt", b"invalid_file_content", content_type="text/plain")
                
                response = self.client.post("/profile/", {"profile": invalid_file}, format="multipart")

                # Refresh the user from the database
                self.user.refresh_from_db()

                # Verify that the profile picture has not changed
                self.assertEqual(self.user.profile.name, old_image)

                # Verify that the response is correct
                self.assertEqual(response.status_code, 400)

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
