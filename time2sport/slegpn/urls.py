from django.urls import path, include
from . import views
from django.contrib import admin
from django.conf import settings


urlpatterns = [
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/<int:notification_id>/read/', views.mark_as_read, name='mark_as_read'),
    path('notifications/unread-count/', views.unread_notifications_count, name='unread_notifications_count'),

    path('activities/<int:activity_id>/invoice/', views.invoice_activity, name='invoice_activity'),
    path('facilities/<int:facility_id>/invoice/', views.invoice_facility, name='invoice_facility'),

    path('enrollment/<int:bonus_id>/', views.complete_enrollment, name='complete_enrollment'),
    path('payment-activity-success/<int:product_bonus_id>/', views.payment_activity_successful, name='payment-activity-success'),
    path('payment-activity-failed/<int:bonus_id>/', views.payment_activity_failed, name='payment-activity-failed'),

    path('payment-facility-success/<int:facility_id>/', views.payment_facility_successful, name='payment-facility-success'),
    path('payment-facility-failed/<int:facility_id>/', views.payment_facility_failed, name='payment-facility-failed'),

    path('waiting-list/', views.waiting_list, name='waiting-list'),
    path('waiting-list/cancel/<int:waiting_list_id>/', views.cancel_waiting_list, name='cancel_waiting_list'),
    path('wait-list/<int:session_id>/', views.join_waiting_list, name='join_waiting_list'),


    path('', include('paypal.standard.ipn.urls')),
]
