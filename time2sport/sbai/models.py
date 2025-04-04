from django.db import models
import os

def photo_upload_path(instance, filename):
    # Si la imagen pertenece a una actividad, guardarla en "activities/{id}"
    if instance.activity:
        return f"activities/{instance.activity.id}/{filename}"
    
    # Si la imagen pertenece a una instalación, guardarla en "facilities/{id}"
    elif instance.facility:
        return f"facilities/{instance.facility.id}/{filename}"
    
    # Si no pertenece a ninguna, guardarla en "photos"
    return f"photos/{filename}"

class Schedule(models.Model):
    DAYS_OF_WEEK = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    ]

    day_of_week = models.CharField(max_length=10, choices=DAYS_OF_WEEK)
    hour_begin = models.TimeField()
    hour_end = models.TimeField()

    def __str__(self):
        return f"{self.day_of_week}: {self.hour_begin} - {self.hour_end}"


class SportFacility(models.Model):
    FACILITY_TYPE_CHOICES = [
        ('exterior', 'Exterior'),
        ('interior', 'Interior'),
    ]

    name = models.CharField(max_length=255)
    number_of_facilities = models.IntegerField()
    description = models.TextField()
    hour_price = models.FloatField()
    facility_type = models.CharField(max_length=10, choices=FACILITY_TYPE_CHOICES)
    schedules = models.ManyToManyField(Schedule, related_name="sport_facilities", blank=True)

    def save(self, *args, **kwargs):
        if not self.pk and self.number_of_facilities > 1 and not kwargs.pop("skip_duplication", False):
            super().save(*args, **kwargs)

            base_name = self.name
            schedules_copy = list(self.schedules.all())

            for i in range(1, self.number_of_facilities + 1):
                instance = SportFacility(
                    name=f"{base_name} {i}",
                    number_of_facilities=1,
                    description=self.description,
                    hour_price=self.hour_price,
                    facility_type=self.facility_type
                )
                instance.save()
                instance.schedules.set(schedules_copy)
        else:
            super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Activity(models.Model):
    ACTIVITY_TYPE_CHOICES = [
        ('terrestre', 'Terrestre'),
        ('acuática', 'Acuática'),
    ]

    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    description = models.TextField()
    activity_type = models.CharField(max_length=15, choices=ACTIVITY_TYPE_CHOICES)
    schedules = models.ManyToManyField(Schedule, related_name="activities", blank=True)

    def __str__(self):
        return self.name


class Photo(models.Model):
    activity = models.ForeignKey("Activity", related_name='photos', on_delete=models.CASCADE, null=True, blank=True)
    facility = models.ForeignKey("SportFacility", related_name='photos', on_delete=models.CASCADE, null=True, blank=True)
    image = models.ImageField(upload_to=photo_upload_path)

    def __str__(self):
        return f"Photo {self.id}"


class Bonus(models.Model):
    BONUS_TYPE_CHOICES = [
        ('annual', 'Bono Anual'),
        ('semester', 'Bono Semestral'),
        ('single', 'Bono Sesión Única'),
    ]

    id = models.AutoField(primary_key=True)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name="bonuses")
    bonus_type = models.CharField(max_length=10, choices=BONUS_TYPE_CHOICES)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.get_bonus_type_display()} - {self.activity.name}"
