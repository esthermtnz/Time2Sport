from django.db import models
import os
from enum import Enum

def photo_upload_path(instance, filename):
    ''' Function to define the upload path for photos. '''

    # If the image belongs to an activity, save it in "activities/{id}"
    if instance.activity:
        return f"activities/{instance.activity.id}/{filename}"
    
    # If the image belongs to a facility, save it in "facilities/{id}"
    elif instance.facility:
        return f"facilities/{instance.facility.id}/{filename}"
    
    # If it doesn't belong to any, save it in "photos"
    return f"photos/{filename}"


class DayOfWeek(models.IntegerChoices):
    """ Class to represent the days of the week. """
    LUNES = 0, "Lunes"
    MARTES = 1, "Martes"
    MIERCOLES = 2, "Miércoles"
    JUEVES = 3, "Jueves"
    VIERNES = 4, "Viernes"
    SABADO = 5, "Sabado"
    DOMINGO = 6, "Domingo"

class Schedule(models.Model):
    """ Class to represent the schedule of a sport facility or activity. """
    day_of_week = models.IntegerField(choices=DayOfWeek.choices)
    hour_begin = models.TimeField()
    hour_end = models.TimeField()

    def __str__(self):
        return f"{self.get_day_of_week_display()}: {self.hour_begin} - {self.hour_end}"


class SportFacilityManager(models.Manager):
    ''' Custom manager for the SportFacility model used for overriding the create method. '''
    def create(self, name, number_of_facilities, description, hour_price, facility_type, schedules=None, **kwargs):
        instances = []
        # If the number of facilities is greater than 1, create a list of names
        if number_of_facilities > 1:
            original_name = name
            for i in range(1, number_of_facilities + 1):
                if i == 1:
                    name = original_name
                else:
                    name = f"{original_name} {i}"
                instances.append(name)
        else:
            instances.append(name)

        created_facilities = []
        count = 0
        # Iterate through the list of names and create a facility for each
        for i in instances:
            # If a facility with the same name does not exist, create it
            if not self.model.objects.filter(name=i).exists():
                facility = self.model(
                    name=i,
                    number_of_facilities=number_of_facilities,
                    description=description,
                    hour_price=hour_price,
                    facility_type=facility_type
                )
                facility.save()

                # If schedules are provided, set them for the facility
                if schedules:
                    facility.schedules.set(schedules)
                    facility.save()

                created_facilities.append(facility)
                count += 1

        return created_facilities[0]


class SportFacility(models.Model):
    """ Class to represent a sport facility. """

    # Define the choices for the facility type
    FACILITY_TYPE_CHOICES = [
        ('exterior', 'Exterior'),
        ('interior', 'Interior'),
    ]

    name = models.CharField(max_length=255)
    number_of_facilities = models.IntegerField()
    description = models.TextField()
    hour_price = models.DecimalField(max_digits=6, decimal_places=2)
    facility_type = models.CharField(max_length=10, choices=FACILITY_TYPE_CHOICES)
    schedules = models.ManyToManyField(Schedule, related_name="sport_facilities", blank=True)

    # Use the custom manager
    objects = SportFacilityManager()

    def __str__(self):
        return self.name


class Activity(models.Model):
    """ Class to represent an activity. """

    # Define the choices for the activity type
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
    """ Class to represent a photo. """
    activity = models.ForeignKey("Activity", related_name='photos', on_delete=models.CASCADE, null=True, blank=True)
    facility = models.ForeignKey("SportFacility", related_name='photos', on_delete=models.CASCADE, null=True, blank=True)
    image = models.ImageField(upload_to=photo_upload_path)

    def __str__(self):
        return f"Photo {self.id}"


class Bonus(models.Model):
    """ Class to represent a bonus. """

    # Define the choices for the bonus type
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
