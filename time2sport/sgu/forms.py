from django import forms

import re


class ContactForm(forms.Form):
    asunto = forms.CharField(
        label="Asunto",
        required=True,
        max_length=180,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Ingrese el asunto del comunicado'})
    )
    nombre = forms.CharField(
        label="Nombre",
        required=True,
        max_length=100,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Ingrese su nombre'})
    )
    email = forms.EmailField(
        label="Email",
        required=True,
        widget=forms.EmailInput(
            attrs={'class': 'form-control', 'placeholder': 'Ingrese su email'})
    )
    contenido = forms.CharField(
        label="Contenido",
        required=True,
        widget=forms.Textarea(
            attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Escriba su mensaje'})
    )


class UAMForm(forms.Form):
    UAM_CHOICES = [
        ("0", "Selecciona una opción"),
        ("1", "No soy de la UAM"),
        ("2", "Soy estudiante de la UAM"),
        ("3", "Soy personal docente o investigador de la UAM"),
        ("4", "Soy PTGAS de la UAM"),
        ("5", "Soy antiguo alumno de la UAM"),
    ]

    user_choice = forms.ChoiceField(
        choices=UAM_CHOICES,
        label="¿Eres de la UAM?",
        widget=forms.Select(
            attrs={'class': 'form-select', 'id': 'user_choice'})
    )

    email_uam = forms.EmailField(
        required=False,
        label="Correo institucional de la UAM",
        widget=forms.EmailInput(attrs={
                                'class': 'form-control', 'id': 'email_uam', 'placeholder': 'nombreapellido@uam.es'})
    )

    def clean(self):
        """Cleans the form and verifies that the data introduced is correct"""
        cleaned_data = super().clean()
        user_choice = cleaned_data.get("user_choice")
        email_uam = cleaned_data.get("email_uam")

        if user_choice == "0":
            self.add_error(
                "user_choice", "Debes seleccionar una opción válida.")

        if user_choice in ["2", "3", "4", "5"] and not email_uam:
            self.add_error(
                "email_uam", "Debes ingresar un correo institucional de la UAM.")

        # Filtering if students and staff follow the uam email format
        student_pattern = r"^[a-zA-Z0-9._%+-]+@estudiante\.uam\.es$"
        alumni_pattern = r"^[a-zA-Z0-9._%+-]+@alumni\.uam\.es$"
        staff_pattern = r"^[a-zA-Z0-9._%+-]+@uam\.es$"

        if user_choice == "2" and email_uam and not re.match(student_pattern, email_uam):
            self.add_error(
                "email_uam", "Los estudiantes deben usar un correo @estudiante.uam.es.")
        elif user_choice == "5" and email_uam and not re.match(alumni_pattern, email_uam):
            self.add_error(
                "email_uam", "Los ex-alumnos deben usar un correo @alumni.uam.es.")
        elif user_choice in ["3", "4"] and email_uam and not re.match(staff_pattern, email_uam):
            self.add_error("email_uam", "Debes usar un correo @uam.es.")

        return cleaned_data
