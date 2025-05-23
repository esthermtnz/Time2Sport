from django.urls import path
from .views import reserve_activity_session, check_reserve_facility_session
from .views import reservations, past_reservations, cancel_reservation

urlpatterns = [
    path('reserve/<int:session_id>/', reserve_activity_session,
         name='reserve_activity_session'),
    path('reserve/', check_reserve_facility_session,
         name='check_reserve_facility_session'),
    path('reservations/', reservations, name='reservations'),
    path('past-reservations/', past_reservations, name='past-reservations'),
    path('cancel-reservation/<int:reservation_id>/',
         cancel_reservation, name='cancel_reservation'),
]
