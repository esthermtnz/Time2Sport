from celery import shared_task
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from slegpn.models import WaitingList, Notification
from src.models import Session, Reservation

@shared_task
def check_waiting_list_timeout(session_id):
    session = Session.objects.get(id=session_id)
    waiting_list = session.waiting_list.order_by('join_date')
    current_entry = waiting_list.filter(notified_at__isnull=False).first()

    if current_entry:
        time_limit = current_entry.notified_at + timedelta(minutes=settings.WAITING_LIST_NOTIFICATION_MINS)
        user = current_entry.user

        if timezone.now() > time_limit:
            
            #Checks if the user notified made a reservation
            if Reservation.objects.filter(user=user, session=session).exists():
                current_entry.delete()
            else: 
                Notification.objects.create(
                    user=current_entry.user,
                    title="Tiempo de reserva expirado",
                    content=f"No has confirmado tu plaza en {session.activity.name} a tiempo."
                )
                current_entry.delete()

                #Notify next user
                next_entry = session.waiting_list.filter(notified_at__isnull=True).first()
                if next_entry:
                    next_entry.notified_at = timezone.now()
                    next_entry.save()

                    Notification.objects.create(
                        user=next_entry.user,
                        title="¡Apúntate a la sesión, se ha liberado una plaza!",
                        content=f"Se ha liberado una plaza de {session.activity.name}. Tienes {settings.WAITING_LIST_NOTIFICATION_MINS} minutos para realizar la reserva."
                    )

                    check_waiting_list_timeout.apply_async((session.id,), countdown=settings.WAITING_LIST_NOTIFICATION_MINS*60)
