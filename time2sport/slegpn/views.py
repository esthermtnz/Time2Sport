from django.shortcuts import render, redirect

from django.contrib.auth.decorators import login_required
from slegpn .models import Notification
from django.shortcuts import get_object_or_404

# Create your views here.

@login_required
def notifications(request):

    #REMOVE LATER -- just for testing
    if not request.user.notifications.filter(title='Notificacion de prueba 2').exists():
        Notification.objects.create(
            title='Notificacion de prueba 2',
            content='Esta es una notificacion de prueba 2.',
            user=request.user
        )

    notifications = request.user.notifications.order_by('read', '-timestamp')
    context = {'notifications' : notifications}

    return render(request, 'notifications.html', context)

@login_required
def mark_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.read = True
    notification.save()
    return redirect('notifications')