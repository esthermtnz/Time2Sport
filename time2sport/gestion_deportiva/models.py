from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
import os


class User(AbstractUser):

    def user_directory_path(instance, filename):
        """Generates a unique filename in users"""
        extension = filename.split('.')[-1]  
        filename = f"{instance.id}.{extension}" 
        return os.path.join('users/', filename) 

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text="Unique id for the user")
    profile = models.ImageField(default='default_profile.png', upload_to=user_directory_path)

    def save(self, *args, **kwargs):
        if not self.password:  
            self.set_unusable_password()
        super().save(*args, **kwargs)

    def editProfile(self,image):
        if self.profile and self.profile.name != 'default_profile.png':
            self.profile.delete(save=False)

        self.profile = image
        self.save()
