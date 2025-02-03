from django.shortcuts import render, get_object_or_404
from .models import Activity

def all_activities(request):
    activities = Activity.objects.prefetch_related('photos').all()
    return render(request, 'activities/all_activities.html', {'activities': activities})

def activity_detail(request, activity_id):
    activity = get_object_or_404(Activity, pk=activity_id)
    return render(request, 'activities/activity_detail.html', {'activity': activity})
