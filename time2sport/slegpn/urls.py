from django.urls import path
from . import views
from django.contrib import admin
from django.conf import settings


urlpatterns = [
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/<int:notification_id>/read/', views.mark_as_read, name='mark_as_read'),
    path('activities/<int:activity_id>/invoice/', views.invoice_activity, name='invoice_activity'),
    path('facilities/<int:facility_id>/invoice/', views.invoice_facility, name='invoice_facility'),
]
