from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

'''
FooterTest class which contains the tests for the footer
'''
class FooterTest(TestCase):
    def setUp(self):
        """ Create a user and log in """
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.login(username="testuser", password="testpassword")

    def test_footer_home_page(self):
        """ Verify that the footer is present on the home page """
        # Go to the home page
        response = self.client.get("/home/", follow=True)

        # Check that the footer is present
        self.assertContains(response, "AVISO LEGAL")
        self.assertContains(response, "CONTACTO")
        self.assertContains(response, "POLÍTICA DE PRIVACIDAD")

    def test_footer_legal(self):
        """ Verify the legal page """
        # Go to the legal page
        response = self.client.get("/aviso-legal/", follow=True)

        self.assertContains(response, "Aviso Legal")

    def test_footer_privacy(self):
        """ Verify the privacy page """
        # Go to the privacy page
        response = self.client.get("/politica-privacidad/", follow=True)

        self.assertContains(response, "Política de Privacidad y Protección de Datos Personales")

    def test_footer_contact(self):
        """ Verify the contact page """
        # Go to the contact page
        response = self.client.get("/contacto/", follow=True)
        self.assertContains(response, "Contacto")

        # Send request to contact page with missing fields
        args = {"asunto": "Test"}  # Only the subject is provided
        response = self.client.post("/contacto/", args, follow=True)
        self.assertNotContains(response, "Se ha enviado un correo al administrador con tu petición correctamente. ¡Gracias!")

        args["nombre"] = "testuser"  # Add the name
        response = self.client.post("/contacto/", args, follow=True)
        self.assertNotContains(response, "Se ha enviado un correo al administrador con tu petición correctamente. ¡Gracias!")

        args["email"] = "user@gmail.com"  # Add the email
        response = self.client.post("/contacto/", args, follow=True)
        self.assertNotContains(response, "Se ha enviado un correo al administrador con tu petición correctamente. ¡Gracias!")

        # Send request to contact page with all fields
        args["contenido"] = "Test"  # Add the content
        response = self.client.post("/contacto/", args, follow=True)
        self.assertContains(response, "Se ha enviado un correo al administrador con tu petición correctamente. ¡Gracias!")
