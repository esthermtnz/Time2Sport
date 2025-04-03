from django.shortcuts import render, redirect
from django.urls import reverse

from django.contrib.auth.decorators import login_required
from slegpn .models import Notification
from django.shortcuts import get_object_or_404
from sbai.models import Bonus, Activity, SportFacility
from slegpn.models import ProductBonus
from django.utils import timezone
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings
import uuid

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

        host = request.get_host()

        paypal_checkout = {
            'business': settings.PAYPAL_RECEIVER_EMAIL,
            'amount': total,
            'item_name': bonus_name,
            'invoice': uuid.uuid4(),
            'currency_code': 'EUR',
            'notify_url': f"http://{host}{reverse('paypal-ipn')}",
            'return_url': f"http://{host}{reverse('complete_inscription', kwargs = {'bonus_id': bonus_id})}",
            'cancel_url': f"http://{host}{reverse('payment-failed')}",
        }

        paypal_payment = PayPalPaymentsForm(initial=paypal_checkout)

        context = {
            'bonus_id': bonus_id,
            'concept': activity.name,
            'date': timezone.localtime(),
            'bonus_price':bonus.price,
            'bonus_name': bonus_name,
            'uam_discount': discount,
            'total':total,
            'paypal': paypal_payment,
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

@login_required
def payment_successful(request):
    context={}
    return render(request, 'payments/payment-success.html', context)

@login_required
def payment_failed(request):
    context={}
    return render(request, 'payments/payment-failed.html', context)

@login_required
def complete_inscription(request, bonus_id):
    bonus = get_object_or_404(Bonus, id=bonus_id)
    user = request.user
    date_now = date.today()
    year_now = date_now.year
    month_now = date_now.month

    if not ProductBonus.objects.filter(user=user, bonus=bonus).exists():
        if bonus.bonus_type == 'single':
            product_bonus = ProductBonus.objects.create(user=user, bonus=bonus, one_use_available=True)
        elif bonus.bonus_type == 'semester':

            # ENE - JUN → Second Semester
            if 1 <= month_now <= 6:
                inicio = date(year_now, 1, 1)
                fin = date(year_now, 6, 30)

            # JUL - DIC → First Semester
            elif 7 <= month_now <= 12:
                inicio = date(year_now, 9, 1)
                fin = date(year_now, 12, 31)

            product_bonus = ProductBonus.objects.create(user=user, bonus=bonus, date_begin=inicio, date_end=fin)
        elif bonus.bonus_type == 'annual':
            product_bonus = ProductBonus.objects.create(user=user, bonus=bonus, date_begin=date(year_now, 9, 1), date_end=date((year_now+1), 6, 30))

        print(product_bonus)
        return redirect('payment-success')
    
    return redirect('home')
