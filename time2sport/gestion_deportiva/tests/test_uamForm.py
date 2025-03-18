from django.test import TestCase
from gestion_deportiva.forms import UAMForm
from django.contrib.auth import get_user_model

User = get_user_model()

"""
UAMFormTestCase class which contains the tests for the UAM form
"""
class UAMFormTestCase(TestCase):
    # Option 0
    def test_no_valid_option(self):
        """ It should fail if the selected option is 'Selecciona una opción' """

        form = UAMForm(data={"user_choice": "0", "email_uam": ""})
        self.assertFalse(form.is_valid())
        self.assertIn("user_choice", form.errors)

    def test_uam_option_without_email(self):
        """ It should fail if a UAM option is selected but no email is entered """

        form = UAMForm(data={"user_choice": "2", "email_uam": ""})
        self.assertFalse(form.is_valid())
        self.assertIn("email_uam", form.errors)

        form = UAMForm(data={"user_choice": "3", "email_uam": ""})
        self.assertFalse(form.is_valid())
        self.assertIn("email_uam", form.errors)

        form = UAMForm(data={"user_choice": "4", "email_uam": ""})
        self.assertFalse(form.is_valid())
        self.assertIn("email_uam", form.errors)

        form = UAMForm(data={"user_choice": "5", "email_uam": ""})
        self.assertFalse(form.is_valid())
        self.assertIn("email_uam", form.errors)

    # Option 1
    def test_external_user_without_email(self):
        """ It should pass if the user selects 'No soy de la UAM' """

        form = UAMForm(data={"user_choice": "1", "email_uam": ""})
        self.assertTrue(form.is_valid())

    # Option 2
    def test_student_with_valid_email(self):
        """ It should pass if the student uses an @estudiante.uam.es email """

        form = UAMForm(data={"user_choice": "2", "email_uam": "user@estudiante.uam.es"})
        self.assertTrue(form.is_valid())

    def test_student_with_invalid_email(self):
        """ It should fail if a student uses an incorrect email """

        form = UAMForm(data={"user_choice": "2", "email_uam": "user@uam.es"})
        self.assertFalse(form.is_valid())

        form = UAMForm(data={"user_choice": "2", "email_uam": "user@gmail.com"})
        self.assertFalse(form.is_valid())

    # Option 3
    def test_professor_researcher_with_valid_email(self):
        """ It should pass if the professor or researcher uses an @uam.es email """

        form = UAMForm(data={"user_choice": "3", "email_uam": "user@uam.es"})
        self.assertTrue(form.is_valid())

    def test_professor_researcher_with_invalid_email(self):
        """ It should fail if the professor or researcher uses an incorrect email """

        form = UAMForm(data={"user_choice": "3", "email_uam": "user@estudiante.uam.es"})
        self.assertFalse(form.is_valid())

        form = UAMForm(data={"user_choice": "3", "email_uam": "user@gmail.com"})
        self.assertFalse(form.is_valid())

    # Option 4
    def test_administrative_staff_with_valid_email(self):
        """ It should pass if the administrative staff uses an @uam.es email """

        form = UAMForm(data={"user_choice": "4", "email_uam": "user@uam.es"})
        self.assertTrue(form.is_valid())

    def test_administrative_staff_with_invalid_email(self):
        """ It should fail if the administrative staff uses an incorrect email """

        form = UAMForm(data={"user_choice": "4", "email_uam": "user@estudiante.uam.es"})
        self.assertFalse(form.is_valid())

        form = UAMForm(data={"user_choice": "4", "email_uam": "user@gmail.com"})
        self.assertFalse(form.is_valid())

    # Option 5
    def test_old_student_with_valid_email(self):
        """ It should pass if the former student uses an @uam.es email """

        form = UAMForm(data={"user_choice": "5", "email_uam": "user@uam.es"})
        self.assertTrue(form.is_valid())

    def old_student_with_invalid_email(self):
        """ It should fail if the former student uses an incorrect email """

        form = UAMForm(data={"user_choice": "5", "email_uam": "user@estudiante.uam.es"})
        self.assertFalse(form.is_valid())

        form = UAMForm(data={"user_choice": "5", "email_uam": "user@gmail.com"})
        self.assertFalse(form.is_valid())
