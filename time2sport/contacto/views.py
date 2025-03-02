from django.shortcuts import render, redirect
from .forms import ContactForm
from django.core.mail import EmailMessage

# Create your views here.
def contacto(request):
    contactForm = ContactForm()

    if request.method == "POST":
        contactForm = ContactForm(data=request.POST)

        if contactForm.is_valid():
            asunto = request.POST.get("asunto")
            nombre = request.POST.get("nombre")
            email = request.POST.get("email")
            contenido = request.POST.get("contenido")

            mensaje_html = f"""
                <html>
                    <body>
                        <p>Hola,</p>
                        <p>Has recibido un nuevo mensaje a través del formulario de contacto.</p>
                        <p><strong>📌 Asunto:</strong> {asunto}</p>
                        <p><strong>👤 Nombre:</strong> {nombre}</p>
                        <p><strong>📧 Correo electrónico:</strong> {email}</p>
                        <hr>
                        <p><strong>📝 Mensaje:</strong></p>
                        <p>{contenido}</p>
                        <hr>
                        <p>Este mensaje ha sido enviado desde el formulario de contacto de Time2Sport.</p>
                    </body>
                </html>
            """

            emailMessage = EmailMessage(asunto, mensaje_html, "", ["time2sportuam@gmail.com"], reply_to=[email])
            emailMessage.content_subtype = "html"

            try:
                emailMessage.send()
                return redirect("/contacto/?valido")
            except:
                return redirect("/contacto/?invalido")

    return render(request, 'contacto/contacto.html', {"contactForm": contactForm})


