from django.urls import path
from .views import reserve_activity_session

urlpatterns = [
    path('reserve/<int:session_id>/', reserve_activity_session, name='reserve_activity_session'),
]
