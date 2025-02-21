from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
import uuid


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text="Unique id for the user")
    profile = models.ImageField(upload_to='profiles/', default='default_profile.png')