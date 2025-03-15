import os
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from gestion_deportiva.models import Schedule, SportFacility, Activity, Photo, Bonus

class ModelTests(TestCase):

    def setUp(self):

        # Create a sport facility schedule
        self.sport_facility_schedule = Schedule.objects.create(
            day_of_week = "Wednesday",
            hour_begin = "09:00:00",
            hour_end = "11:00:00"
        )

        # Create an activity schedule
        self.activity_schedule = Schedule.objects.create(
            day_of_week = "Tuesday",
            hour_begin = "08:00:00",
            hour_end = "14:00:00"
        )

        # Create a sport facility
        self.sport_facility = SportFacility.objects.create(
            name = "Campo de Fútbol",
            numberOf_facilities = 2,
            description = "Campo de fútbol sala para fútbol 5",
            hour_price = 25.0,
            facility_type = "exterior"
        )
        self.sport_facility.schedules.add(self.sport_facility_schedule)

        # Create an activity
        self.activity = Activity.objects.create(
            name = "Zumba",
            location = "Sala 4",
            description = "Zumba coreografiada para jóvenes",
            activity_type = "terrestre",
        )
        self.activity.schedules.add(self.activity_schedule)

        #Create a bonus
        self.bonus = Bonus.objects.create(
            activity=self.activity,
            bonus_type="annual",
            price=100.00
        )

    def test_schedule_creation(self):
        """Verificar que el horario se crea correctamente"""
        self.assertEqual(str(self.sport_facility_schedule), "Wednesday: 09:00:00 - 11:00:00")

    def test_sport_facility_creation(self):
        """Verificar que la instalación se crea correctamente"""
        self.assertEqual(str(self.sport_facility), "Campo de Fútbol")
        self.assertEqual(self.sport_facility.numberOf_facilities, 2)

    def test_activity_creation(self):
        """Verificar que la actividad se crea correctamente"""
        self.assertEqual(str(self.activity), "Zumba")
        self.assertEqual(self.activity.activity_type, "terrestre")

    def test_bonus_creation(self):
        """Verificar que el bono se crea correctamente"""
        self.assertEqual(str(self.bonus), "Bono Anual - Zumba")
        self.assertEqual(float(self.bonus.price), 100.00)

    def test_photo_upload_path(self):
        """Verificar que las fotos se guardan en la ruta correcta"""
        image = SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")
        photo = Photo.objects.create(activity=self.activity, image=image)
        
        expected_path = f"activities/{self.activity.id}/test_image.jpg"
        self.assertEqual(photo.image.name, expected_path)

        image_path = photo.image.path  

        photo.delete()

        if os.path.exists(image_path):
            os.remove(image_path)

    
