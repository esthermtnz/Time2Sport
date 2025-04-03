from django.shortcuts import render, redirect, get_object_or_404

from .models import Reservation, Session
from django.contrib.auth.decorators import login_required

from django.contrib import messages

@login_required
def reserve_activity_session(request, session_id):
    session = get_object_or_404(Session, id=session_id)
    user = request.user
    reservation = session.add_reservation(user)
    if reservation:
        messages.success(request, "Reserva realizada con éxito.")
    else:
        messages.error(request, "Error al realizar la reserva.")

    return redirect('activity_detail', session.activity.id)
