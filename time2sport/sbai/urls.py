from django.urls import path
from .views import all_activities, activity_detail, all_facilities, facility_detail
from .views import schedules, facilities_schedule, download_facilities_schedule
from .views import activities_schedule, download_activities_schedule
from .views import search_results
from django.contrib import admin
from django.conf import settings

urlpatterns = [
    path('activities/', all_activities, name='all_activities'),
    path('activities/<int:activity_id>/', activity_detail, name='activity_detail'),
    path('facilities/', all_facilities, name='all_facilities'),
    path('facilities/<int:facility_id>/', facility_detail, name='facility_detail'),

    path('schedules/', schedules, name='schedules'),
    path('schedules/facilities/', facilities_schedule, name='facilities_schedule'),
    path('schedules/facilities/download/', download_facilities_schedule, name='download_facilities_schedule'),

    path('schedules/activities/', activities_schedule, name='activities_schedule'),
    path('schedules/activities/download/', download_activities_schedule, name='download_activities_schedule'),

    path('search/', search_results, name='search_results'),
]
