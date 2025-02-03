from django.urls import path
from .views import all_activities, activity_detail

urlpatterns = [
    path('activities/', all_activities, name='all_activities'),
    path('activities/<int:activity_id>/', activity_detail, name='activity_detail'),
]
