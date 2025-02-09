from django.urls import path
from .views import all_activities, activity_detail, all_facilities, facility_detail
from .views import home

urlpatterns = [
    path('activities/', all_activities, name='all_activities'),
    path('activities/<int:activity_id>/', activity_detail, name='activity_detail'),
    path('facilities/', all_facilities, name='all_facilities'),
    path('facilities/<int:facility_id>/', facility_detail, name='facility_detail'),

    path('', home, name='home'),

]
