import os
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from sbai.models import Schedule, SportFacility, Activity, Photo, Bonus, DayOfWeek


class ScheduleModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a sport facility schedule
        cls.sport_facility_schedule = Schedule.objects.create(
            day_of_week=DayOfWeek.MIERCOLES,
            hour_begin="09:00:00",
            hour_end="11:00:00"
        )

        # Create an activity schedule
        cls.activity_schedule = Schedule.objects.create(
            day_of_week=DayOfWeek.MARTES,
            hour_begin="08:00:00",
            hour_end="14:00:00"
        )

    def test_sport_facility_schedule_fields(self):
        """Verify that the sport facility schedule fields match"""
        self.assertEqual(
            self.sport_facility_schedule.get_day_of_week_display(), "Miércoles")
        self.assertEqual(self.sport_facility_schedule.hour_begin, "09:00:00")
        self.assertEqual(self.sport_facility_schedule.hour_end, "11:00:00")

    def test_sport_facility_schedule_str(self):
        """Verify that the sport facility schedule string method is correct"""
        self.assertEqual(str(self.sport_facility_schedule),
                         "Miércoles: 09:00:00 - 11:00:00")

    def test_activity_schedule_fields(self):
        """Verify that the activity schedule fields match"""
        self.assertEqual(
            self.activity_schedule.get_day_of_week_display(), "Martes")
        self.assertEqual(self.activity_schedule.hour_begin, "08:00:00")
        self.assertEqual(self.activity_schedule.hour_end, "14:00:00")

    def test_activity_schedule_str(self):
        """Verify that the activity schedule string method is correct"""
        self.assertEqual(str(self.activity_schedule),
                         "Martes: 08:00:00 - 14:00:00")


class SportFacilityModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a sport facility schedule
        cls.sport_facility_schedule = Schedule.objects.create(
            day_of_week=DayOfWeek.MIERCOLES,
            hour_begin="09:00:00",
            hour_end="11:00:00"
        )

        # Create a sport facility
        cls.sport_facility = SportFacility.objects.create(
            name="Campo de Fútbol",
            number_of_facilities=2,
            description="Campo de fútbol sala para fútbol 5",
            hour_price=25.0,
            facility_type="Exterior"
        )
        cls.sport_facility.schedules.add(cls.sport_facility_schedule)

    def test_sport_facility_fields(self):
        """Verify that the sport facility fields match"""
        self.assertEqual(self.sport_facility.name, "Campo de Fútbol")
        self.assertEqual(self.sport_facility.number_of_facilities, 2)
        self.assertEqual(self.sport_facility.description,
                         "Campo de fútbol sala para fútbol 5")
        self.assertEqual(self.sport_facility.hour_price, 25.0)
        self.assertEqual(self.sport_facility.facility_type, "Exterior")

    def test_sport_facility_schedule(self):
        """Verify that the sport facility schedule is correct"""
        self.assertIn(self.sport_facility_schedule,
                      self.sport_facility.schedules.all())

    def test_sport_facility_str(self):
        """Verify that the sport facility string method is correct"""
        self.assertEqual(str(self.sport_facility), "Campo de Fútbol")


class ActivityModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create an activity schedule
        cls.activity_schedule = Schedule.objects.create(
            day_of_week=DayOfWeek.MARTES,
            hour_begin="08:00:00",
            hour_end="14:00:00"
        )

        # Create an activity
        cls.activity = Activity.objects.create(
            name="Zumba",
            location="Sala 4",
            description="Zumba coreografiada para jóvenes",
            activity_type="Terrestre",
        )
        cls.activity.schedules.add(cls.activity_schedule)

    def test_activity_fields(self):
        """Verify that the activity fields match"""
        self.assertEqual(self.activity.name, "Zumba")
        self.assertEqual(self.activity.location, "Sala 4")
        self.assertEqual(self.activity.description,
                         "Zumba coreografiada para jóvenes")
        self.assertEqual(self.activity.activity_type, "Terrestre")

    def test_activity_schedule(self):
        """Verify that the sport facility schedule is correct"""
        self.assertIn(self.activity_schedule, self.activity.schedules.all())

    def test_activity_str(self):
        """Verify that the activity string method is correct"""
        self.assertEqual(str(self.activity), "Zumba")


class BonusModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create an activity
        cls.activity = Activity.objects.create(
            name="Zumba",
            location="Sala 4",
            description="Zumba coreografiada para jóvenes",
            activity_type="Terrestre",
        )

        # Create a bonus
        cls.bonus = Bonus.objects.create(
            activity=cls.activity,
            bonus_type="annual",
            price=100.00
        )

    def test_bonus_fields(self):
        """Verify that the bonus fields match"""
        self.assertEqual(self.activity, self.bonus.activity)
        self.assertEqual(self.bonus.bonus_type, "annual")
        self.assertEqual(float(self.bonus.price), 100.00)

    def test_bonus_str(self):
        """Verify that the bonus string method is correct"""
        self.assertEqual(str(self.bonus), "Bono Anual - Zumba")


class PhotoModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create an activity
        cls.activity = Activity.objects.create(
            name="Zumba",
            location="Sala 4",
            description="Zumba coreografiada para jóvenes",
            activity_type="Terrestre",
        )

        image = SimpleUploadedFile(
            "test_image.jpg", b"file_content", content_type="image/jpeg")
        # Create a photo
        cls.photo = Photo.objects.create(
            activity=cls.activity,
            image=image
        )

    def test_photo_upload_path(self):
        """Verify that the photo is uploaded in teh correct path"""

        expected_path = f"activities/{self.activity.id}/test_image.jpg"
        self.assertEqual(self.photo.image.name, expected_path)

        image_path = self.photo.image.path

        if os.path.exists(image_path):
            os.remove(image_path)
