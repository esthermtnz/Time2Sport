from django import forms 

class ContactForm(forms.Form):
    asunto = forms.CharField(label="Asunto", required=True, max_length=180)
    nombre = forms.CharField(label="Nombre", required=True)
    email = forms.EmailField(label="Email", required=True)
    contenido = forms.CharField(widget=forms.Textarea, label="Contenido", required=True)
