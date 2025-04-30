from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
import os
from PIL import Image


class User(AbstractUser):
    USER_TYPE_CHOICES = [
        ('notUAM', 'Usuario no perteneciente a la UAM'),
        ('student', 'Estudiante UAM'),
        ('professor', 'Personal docente o investigador UAM'),
        ('administrative', 'Personal Administrativo UAM'),
        ('alumni', 'Ex-alumno de la UAM'),
    ]

    def user_directory_path(instance, filename):
        """Generates a unique filename in users"""
        extension = filename.split('.')[-1]  
        filename = f"{instance.id}.{extension}" 
        return os.path.join('users/', filename) 

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text="Unique id for the user")
    profile = models.ImageField(default='default_profile.png', upload_to=user_directory_path)
    is_uam = models.BooleanField(null=True, blank=True)
    user_type = models.CharField(null=True, max_length=30, choices=USER_TYPE_CHOICES)

    def save(self, *args, **kwargs):
        if not self.password:  
            self.set_unusable_password()
        super().save(*args, **kwargs)

    def editProfile(self, image):
        valid_extensions = {'JPEG', 'JPG', 'PNG'}

        try:
            with Image.open(image) as img:
                image_format = img.format.upper()
                if image_format not in valid_extensions:
                    return

                if self.profile and self.profile.name != 'default_profile.png':
                    self.profile.delete(save=False)

                self.profile = image
                self.save()

        except Exception:
            return

    def has_valid_bono_for_activity(self, activity):
        for bonus in self.bonuses.all():
            if bonus.belongs_to_activity(activity):
                if bonus.is_valid:
                    return True
        return False

    def get_valid_bono_for_activity(self, activity):
        for bonus in self.bonuses.all():
            if bonus.belongs_to_activity(activity):
                if bonus.is_valid:
                    return bonus
        return None
