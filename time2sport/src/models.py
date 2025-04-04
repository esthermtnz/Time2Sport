from django.db import models
from enum import Enum
from django.utils import timezone
from datetime import datetime, date

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

    def add_reservation_activity(self, user):
        # Check if the session is full
        if self.is_full():
            return None

        # Check if the user has a valid bonus for the activity
        if not user.has_valid_bono_for_activity(self.activity):
            return None

        # Check if the user has already reserved for this session
        if Reservation.objects.filter(user=user, session=self).exists():
            return None

        # Get bonus instance if single
        bonus_is_single = ProductBonus.objects.filter(user=user, bonus__activity=self.activity, one_use_available=True).first()

        # Make reservation
        reservation = Reservation.objects.create(user=user, session=self, status=ReservationStatus.VALID.value)
        self.free_places -= 1

        # If bonus is single-use, mark it as used
        if bonus_is_single:
            bonus_is_single.use_single_use()

        reservation.save()

        self.save()
        return reservation

    def add_reservation_facility(self, user):
        # Check if the session is full
        if self.is_full():
            return None

        # Check if the user has already reserved for this session
        if Reservation.objects.filter(user=user, session=self).exists():
            return None

        # Make reservation
        reservation = Reservation.objects.create(user=user, session=self, status=ReservationStatus.VALID.value)
        self.free_places -= 1

        reservation.save()

        self.save()
        return reservation

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



class ProductBonus(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bonuses')
    bonus = models.ForeignKey(Bonus, on_delete=models.CASCADE, related_name='purchases')
    purchase_date = models.DateTimeField(default=timezone.now)
    date_begin = models.DateField(null=True, blank=True)
    date_end = models.DateField(null=True, blank=True)
    one_use_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - {self.bonus.get_bonus_type_display()} ({'Válido' if self.is_valid else 'No válido'})"

    @property
    def is_valid(self):
        date_now = timezone.now().date()
        type = self.bonus.bonus_type

        if type == 'single':
            print("Single use bonus", self.one_use_available)
            return self.one_use_available  
        elif type in ['annual', 'semester']:
            return self.date_begin and self.date_end and self.date_begin <= date_now <= self.date_end
        return False

    def use_single_use(self):
        if self.bonus.bonus_type == 'single':
            self.one_use_available = False
            self.save()

    def cancel_single_use(self):
        if self.bonus.bonus_type == 'single':
            self.one_use_available = True
            self.save()

    def belongs_to_activity(self, activity):
        return self.bonus.activity == activity
