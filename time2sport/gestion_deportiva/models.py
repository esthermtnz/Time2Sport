from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text="Unique id for the user")
    profile = models.ImageField(default='default_profile.png', upload_to='users/')
    
    def save(self, *args, **kwargs):
        if not self.password:  # Evita requerir contraseña si está vacía
            self.set_unusable_password()
        super().save(*args, **kwargs)
