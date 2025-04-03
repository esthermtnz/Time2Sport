from django.shortcuts import render, redirect, get_object_or_404

from .models import Reservation, Session
from django.contrib.auth.decorators import login_required

from django.contrib import messages
from sbai.models import Bonus
from .models import ProductBonus

@login_required
def reserve_activity_session(request, session_id):
    session = get_object_or_404(Session, id=session_id)
    if session is None:
        return redirect('all_activities')

    user = request.user
    reservation = session.add_reservation(user)
    if reservation:
        messages.success(request, "Reserva realizada con éxito.")
    else:
        messages.error(request, "Error al realizar la reserva.")

    return redirect('activity_detail', session.activity.id)


def purchase_bonus(request, bonus_id):
    bonus = get_object_or_404(Bonus, id=bonus_id)

    activity = bonus.activity
    user = request.user

    # Verificar si el usuario ya tiene un bono válido para la actividad
    if user.has_valid_bono_for_activity(activity):
        messages.error(request, "Ya tienes un bono para esta actividad.")
        return redirect('activity_detail', activity_id=activity.id)

    bonoPurchase = ProductBonus.objects.create(user=user, bonus=bonus)
    bonoPurchase.save()

    messages.success(request, "Bono comprado con éxito!")
    return redirect('activity_detail', activity_id=activity.id)
