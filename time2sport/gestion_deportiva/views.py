from django.shortcuts import render, get_object_or_404
from .models import Activity, SportFacility

def all_activities(request):
    activities = Activity.objects.prefetch_related('photos').all()
    return render(request, 'activities/all_activities.html', {'activities': activities})

def activity_detail(request, activity_id):
    activity = get_object_or_404(Activity, pk=activity_id)
    return render(request, 'activities/activity_detail.html', {'activity': activity})

def all_facilities(request):
    facilities = SportFacility.objects.prefetch_related('photos').all()
    return render(request, 'facilities/all_facilities.html', {'facilities': facilities})

def facility_detail(request, facility_id):
    facility = get_object_or_404(SportFacility, pk=facility_id)
    return render(request, 'facilities/facility_detail.html', {'facility': facility})

def home(request):
    return render(request, 'home.html')
