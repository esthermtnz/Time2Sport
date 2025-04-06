from django.db import models
from sgu.models import User
from sbai.models import Bonus
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
    

class ProductBonus(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bonuses')
    bonus = models.ForeignKey(Bonus, on_delete=models.CASCADE, related_name='purchases')
    purchase_date = models.DateTimeField(default=timezone.now)
    date_begin = models.DateField(null=True, blank=True)
    date_end = models.DateField(null=True, blank=True)
    one_use_available = models.BooleanField(default=True)

    def __str__(self):
         return f"{self.user.username} - {self.bonus.get_bonus_type_display()} ({'Válido' if self.is_valid else 'No válido'})"
    
    @property
    def is_valid(self):
        date_now = timezone.now().date()
        type = self.bonus.bonus_type

        if type == 'single':
            return self.one_use_available  
        elif type in ['annual', 'semester']:
            return self.date_begin and self.date_end and self.date_begin <= date_now <= self.date_end
        return False