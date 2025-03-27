from django.urls import path
from . import views
from django.contrib import admin
from django.conf import settings


urlpatterns = [
    path('', views.log_in, name='log_in'),
    path('log_out/', views.log_out, name='log_out'),
    path('home/', views.index, name='index'),
    path('profile/', views.profile, name='profile'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('aviso-legal/', views.aviso_legal, name='aviso_legal'),
    path('politica-privacidad/', views.politica_privacidad, name='politica_privacidad'),
    path('contacto/', views.contacto, name='contacto'),
    path('uam-verification/', views.uam_verification, name='uam_verification'),
    path('verificar-codigo-uam/', views.verificar_codigo_uam, name='verificar_codigo_uam'),
    
]
