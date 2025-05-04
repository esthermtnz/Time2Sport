from django.shortcuts import render, redirect, get_object_or_404

from .models import Reservation, Session
from django.conf import settings
from django.contrib.auth.decorators import login_required

from django.contrib import messages
from sbai.models import Bonus, SportFacility, Schedule
from src.models import Reservation
from slegpn.models import ProductBonus, Notification, WaitingList
from slegpn.tasks import check_waiting_list_timeout

from datetime import datetime, date
from django.utils.timezone import now


def _is_conflict_reserved_sessions(users_sessions_day, requested_start, requested_end):
    ''' Check if the user has another session at the same time '''

    for reserved in users_sessions_day:
        reserved_start = reserved.session.start_time
        reserved_end = reserved.session.end_time

        # If it starts when another sessionn is happening
        if requested_start < reserved_end and requested_end > reserved_start:
            return True
    return False


def _is_conflict_chosen_sessions(selected_sessions):
    ''' Check if the user has chosen sessions that overlap each other '''

    session_times = []

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
    ''' Get the session data from the session string '''
    facility_id, start, end, day = session.split('|')
    day = datetime.strptime(day, "%B %d %Y")
    requested_start = datetime.strptime(start, '%H:%M').time()
    requested_end = datetime.strptime(end, '%H:%M').time()

    return facility_id, day, requested_start, requested_end


@login_required
def reserve_activity_session(request, session_id):
    ''' Reserve an activity session '''
    session = get_object_or_404(Session, id=session_id)
    if session is None:
        return redirect('all_activities')

    user = request.user

    # Check if the user does not have another session at the same time
    users_sessions_day = user.reservations.filter(session__date=session.date)
    requested_start = session.start_time
    requested_end = session.end_time

    if _is_conflict_reserved_sessions(users_sessions_day, requested_start, requested_end):
        messages.error(
            request, "Ya tienes una reserva para esa hora. Puedes ver tus reservas en la sección de 'Mis Reservas'.")
        return redirect('activity_detail', session.activity.id)

    reservation = session.add_reservation_activity(user)
    if reservation:
        messages.success(request, "Reserva realizada con éxito.")
        title = "Reserva realizada con éxito"
        content = f"Has realizado una reserva de {session.activity} para el día {session.date.strftime('%d/%m/%Y')}."
        Notification.objects.create(user=user, title=title, content=content)

        # If user was in the waiting list delete entry
        WaitingList.objects.filter(user=user, session=session).delete()
    else:
        messages.error(request, "Error al realizar la reserva.")

    return redirect('activity_detail', session.activity.id)


@login_required
def check_reserve_facility_session(request):
    ''' Check if the user can reserve the facility session '''
    if request.method == 'POST':
        selected_sessions = [s for s in request.POST.get(
            'selected_sessions', '').split(',') if s]
        request.session['selected_sessions'] = selected_sessions

        # Check if the user has selected sessions
        if not selected_sessions:
            messages.error(request, 'No se ha seleccionado ninguna sesión.')
            return redirect('facility_detail', facility_id=request.POST.get('facility_id'))

        # Check if the user has selected sessions that overlap each other
        if _is_conflict_chosen_sessions(selected_sessions):
            messages.error(request, "Las reservas seleccionadas se solapan.")
            return redirect('facility_detail', facility_id=request.POST.get('facility_id'))

        # Check if the user has already a reservation for the same time
        for session in selected_sessions:
            facility_id, day, requested_start, requested_end = _get_session_split_data(
                session)

            user_sessions = request.user.reservations.filter(session__date=day)

            if _is_conflict_reserved_sessions(user_sessions, requested_start, requested_end):
                messages.error(
                    request, "Ya tienes una reserva para esa hora. Puedes ver tus reservas en la sección de 'Mis Reservas'.")
                return redirect('facility_detail', facility_id=facility_id)

        return redirect('invoice_facility', facility_id=facility_id)


@login_required
def reserve_facility_session(request):
    ''' Reserve the facility session '''
    selected_sessions = request.session['selected_sessions']

    for session in selected_sessions:
        facility_id, start, end, day = session.split('|')

        # Convert date to day of the week
        day_number = datetime.strptime(day, '%B %d %Y').weekday()

        start_time = datetime.strptime(start, '%H:%M').time()
        end_time = datetime.strptime(end, '%H:%M').time()

        # Get the facility and session
        facility = get_object_or_404(SportFacility, id=facility_id)
        session = facility.sessions.filter(
            start_time=start_time, end_time=end_time).first()

        # Check if session is already reserved
        if session and session.free_places > 0:
            Reservation.objects.create(
                session=session,
                user=request.user
            )

            # Update session free places
            session.free_places -= 1
            session.save()

            title = "Reserva realizada correctamente"
            content = f"Has reservado la instalación "

            if facility.number_of_facilities > 1:
                content += ' '.join(facility.name.split(" ")[:-1])
            else:
                content += f"{facility}"
            content += f" el día {session.date.strftime('%d/%m/%Y')}"

        else:
            title = "Error en la reserva"
            content = "Se ha producido un error. Intentelo más tarde"
            messages.error(
                request, f'La hora {start} - {end} ya está ocupada.')

    # Notify the user
    Notification.objects.create(
        title=title, content=content, user=request.user)
    messages.success(request, 'Reserva realizada con éxito.')


@login_required
def reservations(request):
    ''' List all reservations of the user '''
    user = request.user

    reservations = user.reservations.filter(
        session__date__gte=date.today()).order_by('session__date')

    context = {
        'active_tab': 'future_reservations',
        'reservations': reservations
    }

    return render(request, 'reservations.html', context)


@login_required
def past_reservations(request):
    ''' List all past reservations of the user '''
    user = request.user

    past_reservations = user.reservations.filter(
        session__date__lt=date.today()).order_by('-session__date')

    context = {
        'active_tab': 'past_reservations',
        'past_reservations': past_reservations
    }

    return render(request, 'past_reservations.html', context)


@login_required
def cancel_reservation(request, reservation_id):
    ''' Cancel a reservation '''
    reservation = get_object_or_404(
        Reservation, id=reservation_id, user=request.user)
    session = reservation.session

    is_cancelled = reservation.cancel()
    # If the reservation was not cancelled, it means that the user tried to cancel it with less than 2 hours before the session
    if not is_cancelled:
        messages.error(
            request, "No puedes cancelar una reserva con menos de 2 horas de antelación.")
    # The reservation was cancelled
    else:
        # Update the waiting list
        waiting_list = session.waiting_list.order_by('join_date')

        # Find the first user who hasn't been notified
        next_entry = waiting_list.filter(notified_at__isnull=True).first()
        if next_entry:
            # Mark as notified
            next_entry.notified_at = now()
            next_entry.save()

            Notification.objects.create(
                title="¡Apúntate a la sesión, se ha liberado una plaza!",
                content=f"Se ha liberado una plaza en {session.activity.name} para el día {session.date.strftime('%d/%m/%Y')} a las {session.start_time.strftime('%H:%M')}. Tienes {settings.WAITING_LIST_NOTIFICATION_MINS} minutos para confirmar.",
                user=next_entry.user
            )

            # Monitor 20 minutes task
            check_waiting_list_timeout.apply_async(
                (session.id,), countdown=settings.WAITING_LIST_NOTIFICATION_MINS*60)
        messages.success(request, "Reserva cancelada con éxito.")

        if session.activity:
            content = f"Has cancelado tu reserva de {session.activity.name} correctamente."
        elif session.facility:
            content = f"Has cancelado tu reserva de {session.facility.name} correctamente."

        # Notify the user
        title = "Reserva cancelada con éxito"
        Notification.objects.create(
            title=title, content=content, user=request.user)

    return redirect('reservations')
