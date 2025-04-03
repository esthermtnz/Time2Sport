from django.urls import path, include
from . import views
from django.contrib import admin
from django.conf import settings


urlpatterns = [
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/<int:notification_id>/read/', views.mark_as_read, name='mark_as_read'),

    path('activities/<int:activity_id>/invoice/', views.invoice_activity, name='invoice_activity'),
    path('facilities/<int:facility_id>/invoice/', views.invoice_facility, name='invoice_facility'),

    path('payment-success/<int:bonus_id>/', views.complete_inscription, name='complete_inscription'),
    path('payment-success', views.payment_successful, name='payment-success'),
    path('payment-failed', views.payment_failed, name='payment-failed'),

    path('', include('paypal.standard.ipn.urls')),
]
