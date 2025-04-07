from django.urls import path
from .views import reserve_activity_session, purchase_bonus, check_reserve_facility_session

urlpatterns = [
    path('reserve/<int:session_id>/', reserve_activity_session, name='reserve_activity_session'),
    path('purchase_bonus/<int:bonus_id>/', purchase_bonus, name='purchase_bonus'),
    path('reserve/', check_reserve_facility_session, name='check_reserve_facility_session'),
]
