from django.urls import path
from .views import reserve_activity_session, purchase_bonus

urlpatterns = [
    path('reserve/<int:session_id>/', reserve_activity_session, name='reserve_activity_session'),
    path('purchase_bonus/<int:bonus_id>/', purchase_bonus, name='purchase_bonus'),
]
