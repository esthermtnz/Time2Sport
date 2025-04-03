from django.urls import path, include
from . import views
from django.contrib import admin
from django.conf import settings


urlpatterns = [
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/<int:notification_id>/read/', views.mark_as_read, name='mark_as_read'),

    path('activities/<int:activity_id>/invoice/', views.invoice_activity, name='invoice_activity'),
    path('facilities/<int:facility_id>/invoice/', views.invoice_facility, name='invoice_facility'),

    path('enrollment/<int:bonus_id>/', views.complete_enrollment, name='complete_enrollment'),
    path('payment-success/<int:bonus_id>/', views.payment_activity_successful, name='payment-activity-success'),
    path('payment-failed/<int:bonus_id>/', views.payment_activity_failed, name='payment-activity-failed'),

    path('', include('paypal.standard.ipn.urls')),
]
