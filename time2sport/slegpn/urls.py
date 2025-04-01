from django.urls import path
from . import views
from django.contrib import admin
from django.conf import settings


urlpatterns = [
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/<int:notification_id>/read/', views.mark_as_read, name='mark_as_read')
]
