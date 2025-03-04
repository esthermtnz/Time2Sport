from django import forms 

class ContactForm(forms.Form):
    asunto = forms.CharField(
        label="Asunto", 
        required=True, 
        max_length=180,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el asunto del comunicado'})
    )
    nombre = forms.CharField(
        label="Nombre", 
        required=True,
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese su nombre'})
    )
    email = forms.EmailField(
        label="Email", 
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese su email'})
    )
    contenido = forms.CharField(
        label="Contenido", 
        required=True,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Escriba su mensaje'})
    )
