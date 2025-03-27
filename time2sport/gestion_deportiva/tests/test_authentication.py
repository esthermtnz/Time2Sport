from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class AuthenticationTest(TestCase):
    def test_logout_without_authentication(self):
        """ Verify that logout works even if no user is logged in """
        response = self.client.post("/accounts/logout/")
        self.assertRedirects(response, "/")

    def test_login_google_then_logout(self):
        """ Verify that a user can log in with Google and then log out successfully """

        # Verify that the Google login URL redirects to Google's authentication page
        response = self.client.get("/accounts/google/login/")
        self.assertIn("https://accounts.google.com/o/oauth2/v2/auth", response["Location"])

        # Create and log in a test user
        user = User.objects.create_user(email="user@gmail.com", username="testuser")
        self.client.force_login(user)

        # Verify that the user is authenticated
        response = self.client.get(reverse("profile"))
        self.assertTrue(response.context["user"].is_authenticated)
        self.assertEqual(response.context["user"].email, "user@gmail.com")

        # Verify that the authenticated user matches the created user 
        self.assertEqual(self.client.session["_auth_user_id"], str(user.id))

        # Ensure that the user exists in the database
        self.assertTrue(User.objects.filter(email="user@gmail.com").exists())

        # Perform logout
        response = self.client.post("/accounts/logout/")
        self.assertRedirects(response, "/")

    def test_login_microsoft_then_logout(self):
        """ Verify that a user can log in with Google and then log out successfully """

        # Verify that the Microsoft login URL redirects to Microsoft's authentication page
        response = self.client.get("/accounts/microsoft/login/")
        self.assertIn("https://login.microsoftonline.com/consumers/oauth2/v2.0/authorize", response["Location"])

        # Create and log in a test user
        user = User.objects.create_user(email="user@gmail.com", username="testuser")
        self.client.force_login(user)

        # Verify that the user is authenticated
        response = self.client.get(reverse("profile"))
        self.assertTrue(response.context["user"].is_authenticated)
        self.assertEqual(response.context["user"].email, "user@gmail.com")

        # Verify that the authenticated user matches the created user 
        self.assertEqual(self.client.session["_auth_user_id"], str(user.id))

        # Ensure that the user exists in the database
        self.assertTrue(User.objects.filter(email="user@gmail.com").exists())

        # Perform logout
        response = self.client.post("/accounts/logout/")
        self.assertRedirects(response, "/")
