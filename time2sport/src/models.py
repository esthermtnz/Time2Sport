from django.db import models
from enum import Enum
from django.utils import timezone
from datetime import datetime, date
from datetime import timedelta

from sbai.models import *
from sgu.models import User

class Session(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name="sessions", null=True)
    facility = models.ForeignKey(SportFacility, on_delete=models.CASCADE, related_name="sessions", null=True)
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    capacity = models.IntegerField(default=1)
    free_places = models.IntegerField(default=1)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()


    def is_full(self):
        return self.free_places == 0

    def add_reservation_activity(self, user):
        from slegpn.models import ProductBonus
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


    @staticmethod
    def create_sessions(schedules, activity=None, facility=None, capacity=10):
        if (activity and facility) or (not activity and not facility):
            return []

        sessions = []
        today = datetime.today()

        if activity:
            for schedule in schedules:
                day_of_week = schedule.day_of_week
                target_day_index = int(day_of_week)
                today_day_index = today.weekday()

                days_diff = target_day_index - today_day_index
                if days_diff <= 0:
                    days_diff += 7

                first_session_date = today + timedelta(days=days_diff)

                date = first_session_date
                session = Session.objects.create(
                    activity=activity,
                    facility=None,
                    schedule=schedule,
                    date=first_session_date,
                    capacity=capacity,
                    free_places=capacity,
                    start_time=schedule.hour_begin,
                    end_time=schedule.hour_end
                )
                sessions.append(session)

        elif facility:
            if facility.number_of_facilities > 1:
                # Remove last digit from the name
                facility_name = ' '.join(facility.name.split(" ")[:-1])
                instances = SportFacility.objects.filter(name__regex=f"^{facility_name} [0-9]+$")
            else:
                instances = [facility]

            facility_schedules = facility.schedules.all()

            for schedule in schedules:
                if schedule in facility_schedules:
                    sch = facility_schedules.get(day_of_week=schedule.day_of_week, hour_begin=schedule.hour_begin, hour_end=schedule.hour_end)

                    day_of_week = schedule.day_of_week
                    target_day_index = int(day_of_week)
                    today_day_index = today.weekday()

                    # Calculate the difference in days
                    days_diff = target_day_index - today_day_index
                    if days_diff <= 0:
                        days_diff += 7

                    # Calculate the date of the first session
                    first_session_date = today + timedelta(days=days_diff)

                    start_time = schedule.hour_begin
                    end_time = schedule.hour_end
                    start_time = datetime.strptime(start_time, "%H:%M:%S").time()
                    end_time = datetime.strptime(end_time, "%H:%M:%S").time()

                    current_time = datetime.combine(today, start_time)

                    # Divide the time range into 1 hour intervals
                    while current_time.time() < end_time:
                        # Define next time
                        next_time = current_time + timedelta(hours=1)

                        # Create a session for each facility instance
                        for instance in instances:
                            session = Session.objects.create(
                                activity=None,
                                facility=instance,
                                schedule=sch,
                                date=first_session_date,
                                capacity=1,
                                free_places=1,
                                start_time=current_time.time(),
                                end_time=next_time.time()
                            )
                            sessions.append(session)

                        current_time = next_time

        return sessions


    def __str__(self):
        if self.activity is None:
            return f"{self.facility.name} - {self.date.strftime('%d/%m/%Y')} {self.start_time.strftime('%H:%M')}:{self.end_time.strftime('%H:%M')} ({self.free_places}/{self.capacity} disponibles)"
        return f"{self.activity.name} - {self.date.strftime('%d/%m/%Y')} {self.start_time}-{self.end_time} ({self.free_places}/{self.capacity} disponibles)"

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
        from slegpn.models import ProductBonus

        if self.status in [ReservationStatus.VALID.value, ReservationStatus.WAITING_LIST.value]:
            # Comprobar que hay más de 2 horas de antelación
            now = datetime.now()
            session_date_time = datetime.combine(self.session.date, self.session.start_time)
            time_difference = session_date_time - now
            
            if time_difference < timedelta(hours=2):
                return False

            self.session.free_places += 1
            self.session.save()

            if self.session.activity:
                bonusses = ProductBonus.objects.filter(user=self.user, bonus__activity=self.session.activity).last()
                if bonusses.bonus.bonus_type == 'single':
                    bonusses.one_use_available = True
                    bonusses.save()

            self.delete()
            return True

    def __str__(self):
        return f"{self.user.username} - {self.session} ({self.status})"
