from django.shortcuts import render, redirect, get_object_or_404

from .models import Reservation, Session
from django.contrib.auth.decorators import login_required

from django.contrib import messages
from sbai.models import Bonus, SportFacility, Schedule
from src.models import ReservationStatus, Reservation
from slegpn.models import ProductBonus
from django.utils.timezone import now
from datetime import datetime, date

def _is_conflict_reserved_sessions(users_sessions_day, requested_start, requested_end):
    # Check if the user does not have another session at the same time

    for reserved in users_sessions_day:
        reserved_start = reserved.session.start_time
        reserved_end = reserved.session.end_time

        # If it starts when another sessionn is happening
        if requested_start < reserved_end and requested_end > reserved_start:
            return True
    return False

def _is_conflict_chosen_sessions(selected_sessions):
    session_times = []
    # Check that there is no overlapping reservation for those who have just chosen
    for session in selected_sessions:
        facility_id, start, end, day = session.split('|')
        day = datetime.strptime(day, "%B %d %Y")
        requested_start = datetime.strptime(start, '%H:%M').time()
        requested_end = datetime.strptime(end, '%H:%M').time()

        session_times.append((requested_start, requested_end, day))

    for i, session1 in enumerate(session_times):
        start1, end1, day1 = session1
        for j, session2 in enumerate(session_times):

            if i == j:
                continue

            start2, end2, day2 = session2

            if day1 == day2:
                if start1 < end2 and end1 > start2:
                    return True
    return False

def _get_session_split_data(session):
    facility_id, start, end, day = session.split('|')
    day = datetime.strptime(day, "%B %d %Y")
    requested_start = datetime.strptime(start, '%H:%M').time()
    requested_end = datetime.strptime(end, '%H:%M').time()

    return facility_id, day, requested_start, requested_end

@login_required
def reserve_activity_session(request, session_id):
    session = get_object_or_404(Session, id=session_id)
    if session is None:
        return redirect('all_activities')

    user = request.user

    # Check if the user does not have another session at the same time
    users_sessions_day = user.reservations.filter(session__date=session.date)
    requested_start = session.start_time
    requested_end = session.end_time

    if _is_conflict_reserved_sessions(users_sessions_day, requested_start, requested_end):
        messages.error(request, "Ya tienes una reserva para esa hora. Puedes ver tus reservas en la sección de 'Mis Reservas'.")
        return redirect('activity_detail', session.activity.id)

    reservation = session.add_reservation_activity(user)
    if reservation:
        messages.success(request, "Reserva realizada con éxito.")
    else:
        messages.error(request, "Error al realizar la reserva.")

    return redirect('activity_detail', session.activity.id)

@login_required
def purchase_bonus(request, bonus_id):
    bonus = get_object_or_404(Bonus, id=bonus_id)

    activity = bonus.activity
    user = request.user

    # Verificar si el usuario ya tiene un bono válido para la actividad
    if user.has_valid_bono_for_activity(activity):
        messages.error(request, "Ya tienes un bono para esta actividad.")
        return redirect('activity_detail', activity_id=activity.id)

    bonoPurchase = ProductBonus.objects.create(user=user, bonus=bonus)

    # Specify date begin, date end and if of single use
    # If single use
    if bonoPurchase.bonus.bonus_type == "single":
        bonoPurchase.one_use_available = True
    else:
        bonoPurchase.one_use_available = False
        bonoPurchase.date_begin = now().date()
        # If semester bonus
        if bonoPurchase.bonus.bonus_type == "semester":
            # If first semester (September to January)
            if now().month >= 9 and now().month <= 12: # If bought during the first semester
                # end date is january 31 of following year
                bonoPurchase.date_end = datetime(now().year+1, 1, 31).date()
            # If bought after January (second semester)
            else:
                # end date is June 30 of the same year
                bonoPurchase.date_end = datetime(now().year, 6, 30).date()

        # If annual bonus
        else:
            # end date is June 30 of current or following year, deepending on when it was bought
            if now().month >= 1 and now().month <= 6:
                bonoPurchase.date_end = datetime(now().year, 6, 30).date()
            else:
                bonoPurchase.date_end = datetime(now().year+1, 6, 30).date()


    bonoPurchase.save()

    messages.success(request, "Bono comprado con éxito!")
    return redirect('activity_detail', activity_id=activity.id)

@login_required
def reserve_facility_session(request):
    if request.method == 'POST':
        selected_sessions = request.POST.get('selected_sessions', '').split(',')

        if not selected_sessions:
            messages.error(request, 'No se ha seleccionado ninguna sesión.')
            return redirect('facility_detail', facility_id=request.POST.get('facility_id'))

        if _is_conflict_chosen_sessions(selected_sessions):
            messages.error(request, "Las reservas seleccionadas se solapan.")
            return redirect('facility_detail', facility_id=request.POST.get('facility_id'))

        # Check if the user has already a reservation for the same time
        for session in selected_sessions:
            facility_id, day, requested_start, requested_end = _get_session_split_data(session)

            user_sessions = request.user.reservations.filter(session__date=day)

            if _is_conflict_reserved_sessions(user_sessions, requested_start, requested_end):
                messages.error(request, "Ya tienes una reserva para esa hora. Puedes ver tus reservas en la sección de 'Mis Reservas'.")
                return redirect('facility_detail', facility_id=facility_id)

        # <a href="{% url 'invoice_facility' facility.id %}" class="btn btn-success btn-lg">RESERVAR</a>
        # status = render / redirect

        for session in selected_sessions:
            facility_id, start, end, day = session.split('|')

            # Convert date to day of the week
            day_number = datetime.strptime(day, '%B %d %Y').weekday()

            start_time = datetime.strptime(start, '%H:%M').time()
            end_time = datetime.strptime(end, '%H:%M').time()

            # Get the facility and session
            facility = get_object_or_404(SportFacility, id=facility_id)
            session = facility.sessions.filter(start_time=start_time, end_time=end_time).first()

            # Check if session is already reserved
            if session and session.free_places > 0:
                Reservation.objects.create(
                    session=session,
                    user=request.user,
                    status=ReservationStatus.VALID.value
                )
                
                session.free_places -= 1
                session.save()
            else:
                messages.error(request, f'La hora {start} - {end} ya está ocupada.')

        messages.success(request, 'Reserva realizada con éxito.')
    return redirect('facility_detail', facility_id=facility_id)
