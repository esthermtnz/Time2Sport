from django.urls import path
from . import views
from django.contrib import admin
from django.conf import settings

urlpatterns = [
    settings.AUTH.urlpattern,
    path('', views.log_in, name='log_in'),
    path('home/', views.index, name='index'),
    path('profile/', views.profile, name='profile')
]
