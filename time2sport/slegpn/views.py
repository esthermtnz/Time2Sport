from django.shortcuts import render, redirect

from django.contrib.auth.decorators import login_required
from slegpn .models import Notification
from django.shortcuts import get_object_or_404
from sbai.models import Bonus, Activity, SportFacility
from django.utils import timezone
from decimal import Decimal, ROUND_HALF_UP

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

@login_required
def invoice_activity(request, activity_id):
    activity = get_object_or_404(Activity, pk=activity_id)

    if request.method == 'POST':
        bonus_id = request.POST.get('bonus_id')
        bonus = get_object_or_404(Bonus, id=bonus_id)
        total = bonus.price 
        discount = (bonus.price * Decimal('0.1')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        bonus_type_map = {
                    "annual": "Bono Anual",
                    "semester": "Bono Semestral",
                    "single": "Bono Sesión Única",
                }
        
        bonus_name = bonus_type_map.get(bonus.bonus_type)

        if request.user.is_uam:
            total = bonus.price - discount
        context = {
            'concept': activity.name,
            'date': timezone.localtime(),
            'bonus_price':bonus.price,
            'bonus_name': bonus_name,
            'uam_discount': discount,
            'total':total,
        }
    
        return render(request, 'payments/invoice_activity.html', context)
    

    return render(request, 'activities/activity_detail.html', {'activity': activity})

# CHANGE THIS FUNCTION TO SRC RESERVAR PISTA ------- IMPORTANT!!!!
@login_required
def invoice_facility(request, facility_id):
    facility = get_object_or_404(SportFacility, pk=facility_id)

    hour_price = facility.hour_price 
    num_hours = 1 #CHANGE LATER!!!!!
    total = num_hours * hour_price
    renting_price = num_hours * hour_price
    discount = (total * 0.10)

    if request.user.is_uam:
        total = total - discount
    context = {
        'concept': facility.name,
        'date': timezone.localtime(),
        'base_price':hour_price,
        'num_hours': num_hours,
        'renting_price': renting_price,
        'uam_discount': discount,
        'total':total,
    }

    return render(request, 'payments/invoice_facility.html', context)
    
