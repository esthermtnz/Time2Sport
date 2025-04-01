from django.db import models
from sgu.models import User
from django.utils import timezone

# Create your models here.

class Notification(models.Model):
    title = models.CharField(max_length=80)
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    read = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', null=True)

    def __str__(self):
        return f'{self.date} : {self.title} - {self.content}'