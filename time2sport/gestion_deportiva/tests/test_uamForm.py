from django.test import TestCase
from gestion_deportiva.forms import UAMForm
from django.contrib.auth import get_user_model

User = get_user_model()


class UAMFormTestCase(TestCase):
    # Opción 0
    def test_opcion_no_valida(self):
        # Debe fallar si la opción seleccionada es 'Selecciona una opción'
        form = UAMForm(data={"user_choice": "0", "email_uam": ""})
        self.assertFalse(form.is_valid())
        self.assertIn("user_choice", form.errors)

    def test_opcion_uam_sin_correo(self):
        # Debe fallar si se elige una opción UAM pero no se ingresa correo
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

    # Opción 1
    def test_usuario_externo(self):
        # Debe pasar si el usuario elige 'No soy de la UAM'
        form = UAMForm(data={"user_choice": "1", "email_uam": ""})
        self.assertTrue(form.is_valid())

    # Opción 2
    def test_estudiante_con_correo_valido(self):
        # Debe pasar si el estudiante usa un correo @estudiante.uam.es
        form = UAMForm(data={"user_choice": "2", "email_uam": "usuario@estudiante.uam.es"})
        self.assertTrue(form.is_valid())

    def test_estudiante_con_correo_invalido(self):
        # Debe fallar si un estudiante usa un correo incorrecto
        form = UAMForm(data={"user_choice": "2", "email_uam": "usuario@uam.es"})
        self.assertFalse(form.is_valid())

    # Opción 3
    def test_docente_investigador_con_correo_valido(self):
        # Debe pasar si el docente o investigador usa un correo @uam.es
        form = UAMForm(data={"user_choice": "3", "email_uam": "usuario@uam.es"})
        self.assertTrue(form.is_valid())

    def test_docente_investigador_con_correo_invalido(self):
        # Debe fallar si el docente o investigador usa un correo de estudiante
        form = UAMForm(data={"user_choice": "3", "email_uam": "usuario@estudiante.uam.es"})
        self.assertFalse(form.is_valid())

        # Debe fallar si el docente o investigador ingresa un correo externo
        form = UAMForm(data={"user_choice": "3", "email_uam": "usuario@gmail.com"})
        self.assertFalse(form.is_valid())

    # Opción 4
    def test_personal_administrativo_con_correo_valido(self):
        # Debe pasar si el personal administrativo usa un correo @uam.es
        form = UAMForm(data={"user_choice": "4", "email_uam": "usuario@uam.es"})
        self.assertTrue(form.is_valid())

    def test_personal_administrativo_con_correo_invalido(self):
        # Debe fallar si un personal administrativo usa un correo de estudiante
        form = UAMForm(data={"user_choice": "4", "email_uam": "usuario@estudiante.uam.es"})
        self.assertFalse(form.is_valid())

        # Debe fallar si el personal administrativo ingresa un correo externo
        form = UAMForm(data={"user_choice": "4", "email_uam": "usuario@gmail.com"})
        self.assertFalse(form.is_valid())

    # Opción 5
    def test_antiguo_alumno_con_correo_valido(self):
        # Debe pasar si el antiguo alumno usa un correo @uam.es
        form = UAMForm(data={"user_choice": "5", "email_uam": "usuario@uam.es"})
        self.assertTrue(form.is_valid())

    def test_antiguo_alumno_con_correo_invalido(self):
        # Debe fallar si el antiguo alumno usa un correo de estudiante
        form = UAMForm(data={"user_choice": "5", "email_uam": "usuario@estudiante.uam.es"})
        self.assertFalse(form.is_valid())

        # Debe fallar si el antiguo alumno ingresa un correo externo
        form = UAMForm(data={"user_choice": "5", "email_uam": "usuario@gmail.com"})
        self.assertFalse(form.is_valid())
