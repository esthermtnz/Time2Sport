from django.db import models
from enum import Enum

from sbai.models import *
from sgu.models import User

class Session(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name="sessions", null=True)
    facility = models.ForeignKey(SportFacility, on_delete=models.CASCADE, related_name="sessions", null=True)

    schedule = models.OneToOneField(Schedule, on_delete=models.CASCADE)
    capacity = models.IntegerField()
    free_places = models.IntegerField()
    date = models.DateField()

    def is_full(self):
        return self.free_places == 0

    def add_reservation(self, user):

        if not self.is_full():
            reservation = Reservation.objects.create(user=user, session=self, status=ReservationStatus.VALID.value)
            self.free_places -= 1
            self.save()
            return reservation
        return None

    def __str__(self):
        if self.activity is None:
            return f"{self.facility.name} - {self.schedule} ({self.free_places}/{self.capacity} disponibles)"
        return f"{self.activity.name} - {self.schedule} ({self.free_places}/{self.capacity} disponibles)"


class ReservationStatus(Enum):
    VALID = "Valid"
    WAITING_LIST = "Waiting List"
    FINISHED = "Finished"
    CANCELLED = "Cancelled"

class Reservation(models.Model):            
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reservations")
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name="reservations")
    status = models.CharField(max_length=15, choices=[(tag.value, tag.name) for tag in ReservationStatus])

    def cancel(self):
        if self.status in [ReservationStatus.VALID.value, ReservationStatus.WAITING_LIST.value]:
            # Comprobar que hay más de 2 horas de antelación
            
            
            self.status = ReservationStatus.CANCELLED.value
            self.save()
            self.session.free_places += 1
            self.session.save()

    def __str__(self):
        return f"{self.user.username} - {self.session} ({self.status})"
