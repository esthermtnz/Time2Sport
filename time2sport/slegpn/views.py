from django.shortcuts import render, redirect
from django.urls import reverse

from django.contrib.auth.decorators import login_required
from slegpn .models import Notification
from django.shortcuts import get_object_or_404
from sbai.models import Bonus, Activity, SportFacility
from src.views import reserve_facility_session
from slegpn.models import ProductBonus
from sgu.models import User
from django.utils import timezone
from datetime import date
from .utils import get_bonus_name, get_discount, get_total

from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings
import uuid

# Create your views here.

@login_required
def notifications(request):

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
        bonus_name = get_bonus_name(bonus.bonus_type)
        discount = get_discount(bonus.price, request.user.is_uam)
        total = get_total(bonus.price, request.user.is_uam)

        host = request.get_host()

        paypal_checkout = {
            'business': settings.PAYPAL_RECEIVER_EMAIL,
            'amount': total,
            'item_name': bonus_name,
            'invoice': uuid.uuid4(),
            'currency_code': 'EUR',
            'notify_url': f"http://{host}{reverse('paypal-ipn')}",
            'return_url': f"http://{host}{reverse('complete_enrollment', kwargs = {'bonus_id': bonus_id})}",
            'cancel_url': f"http://{host}{reverse('payment-activity-failed', kwargs = {'bonus_id': bonus_id})}",
        }

        paypal_payment = PayPalPaymentsForm(initial=paypal_checkout)

        context = {
            'bonus_id': bonus_id,
            'concept': f'Inscripción {activity.name}',
            'date': timezone.localtime(),
            'bonus_price':bonus.price,
            'bonus_name': bonus_name,
            'uam_discount': discount,
            'total':total,
            'paypal': paypal_payment,
        }
    
        return render(request, 'payments/invoice_activity.html', context)
    

    return render(request, 'activities/activity_detail.html', {'activity': activity})


@login_required
def invoice_facility(request, facility_id):
    facility = get_object_or_404(SportFacility, pk=facility_id)
    selected_sessions = request.session['selected_sessions']

    facility_id = facility.id
    hour_price = facility.hour_price 
    num_hours = len(selected_sessions)
    renting_price = num_hours * hour_price
    discount = get_discount(num_hours * hour_price, request.user.is_uam)
    total = get_total(num_hours * hour_price, request.user.is_uam)


    host = request.get_host()

    paypal_checkout = {
            'business': settings.PAYPAL_RECEIVER_EMAIL,
            'amount': total,
            'item_name': facility.name,
            'invoice': uuid.uuid4(),
            'currency_code': 'EUR',
            'notify_url': f"http://{host}{reverse('paypal-ipn')}",
            'return_url': f"http://{host}{reverse('payment-facility-success', kwargs = {'facility_id': facility_id})}",
            'cancel_url': f"http://{host}{reverse('payment-facility-failed', kwargs = {'facility_id': facility_id})}",
        }

    paypal_payment = PayPalPaymentsForm(initial=paypal_checkout)
    
    context = {
        'concept': f'Alquiler {facility.name}',
        'date': timezone.localtime(),
        'base_price':hour_price,
        'num_hours': num_hours,
        'renting_price': renting_price,
        'uam_discount': discount,
        'total':total,
        'paypal': paypal_payment,
    }

    return render(request, 'payments/invoice_facility.html', context)

@login_required
def complete_enrollment(request, bonus_id):
    bonus = get_object_or_404(Bonus, id=bonus_id)
    user = request.user
    date_now = date.today()
    year_now = date_now.year
    month_now = date_now.month

    if not ProductBonus.objects.filter(user=user, bonus=bonus).exists():
        title = "Pago realizado correctamente"
        content = f"Gracias por inscribirte a {bonus.activity}. "
        content += f"Has pagado {get_total(bonus.price, user.is_uam)}€ en un bono de tipo {get_bonus_name(bonus.bonus_type)}."

        if bonus.bonus_type == 'single':
            content += " Válido para una única reserva de la actividad."
            product_bonus = ProductBonus.objects.create(user=user, bonus=bonus, one_use_available=True)
            Notification.objects.create(user=user, title=title, content=content)
        elif bonus.bonus_type == 'semester':
            # ENE - JUN : Second Semester
            if 1 <= month_now <= 6:
                inicio = date(year_now, 1, 1)
                fin = date(year_now, 6, 30)

            # JUL - DIC : First Semester
            elif 7 <= month_now <= 12:
                inicio = date(year_now, 9, 1)
                fin = date(year_now, 12, 31)

            content += f" Válido de {inicio.strftime('%d/%m/%Y')} - {fin.strftime('%d/%m/%Y')}."
            product_bonus = ProductBonus.objects.create(user=user, bonus=bonus, date_begin=inicio, date_end=fin)
            Notification.objects.create(user=user, title=title, content=content)
        elif bonus.bonus_type == 'annual':
            if 1 <= month_now <= 6:
                inicio = date((year_now-1), 9, 1)
                fin = date(year_now, 6, 30)
            elif 7 <= month_now <= 12:
                inicio = date(year_now, 9, 1)
                fin = date((year_now+1), 6, 30)

            content += f" Válido de {inicio.strftime('%d/%m/%Y')} - {fin.strftime('%d/%m/%Y')}."

            product_bonus = ProductBonus.objects.create(user=user, bonus=bonus, date_begin=inicio, date_end=fin)
            Notification.objects.create(user=user, title=title, content=content)

        return redirect('payment-activity-success', product_bonus_id=product_bonus.id)
    
    return redirect('index')

@login_required
def payment_activity_successful(request, product_bonus_id):
    product_bonus = get_object_or_404(ProductBonus, id=product_bonus_id)
    bonus = get_object_or_404(Bonus, id=product_bonus.bonus.id)
    total = get_total(bonus.price, request.user.is_uam)

    if bonus.bonus_type in ["annual","semester"]:
        validity = f"{product_bonus.date_begin.strftime('%d/%m/%Y')} - {product_bonus.date_end.strftime('%d/%m/%Y')}"
    else:
        validity = "1 reserva"

    context = {
        'concept': f'Inscripción {bonus.activity.name}',
        'total': total,
        'date': timezone.localtime(),
        'validity': validity,
        'activity': bonus.activity,
    }
    return render(request, 'payments/payment-activity-success.html', context)

@login_required
def payment_activity_failed(request, bonus_id):
    product_bonus = get_object_or_404(ProductBonus, id=bonus_id)
    bonus = get_object_or_404(Bonus, id=product_bonus.bonus.id)
    total = get_total(bonus.price, request.user.is_uam)
    context={
        'concept': f'Inscripción {bonus.activity.name}',
        'total': total,
        'date': timezone.localtime(),
    }
    return render(request, 'payments/payment-activity-failed.html', context)


@login_required
def payment_facility_successful(request, facility_id):
    facility = get_object_or_404(SportFacility, id=facility_id)
    num_hours = len(request.session['selected_sessions'])
    total = get_total(num_hours * facility.hour_price, request.user.is_uam)

    context = {
        'concept': f'Alquiler {facility.name}',
        'date': timezone.localtime(),
        'total':total,
    }

    reserve_facility_session(request)
    return render(request, 'payments/payment-facility-success.html', context)

@login_required
def payment_facility_failed(request, facility_id):
    facility = get_object_or_404(SportFacility, id=facility_id)
    num_hours = len(request.session['selected_sessions'])
    total = get_total(num_hours * facility.hour_price, request.user.is_uam)

    context={
        'concept': f'Inscripción {facility.name}',
        'date': timezone.localtime(),
        'total': total,
    }
    return render(request, 'payments/payment-facility-failed.html', context)
