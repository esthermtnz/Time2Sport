from django.db import models
from sgu.models import User
from sbai.models import Bonus
from django.utils import timezone

# Create your models here.


class Notification(models.Model):
    """Class representing a notification"""
    title = models.CharField(max_length=80)
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    read = models.BooleanField(default=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='notifications', null=True)

    def __str__(self):
        return f'{self.timestamp} : {self.title} - {self.content}'


class ProductBonus(models.Model):
    """Class representing the bonus purchased after the inscription of an activity"""
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='bonuses')
    bonus = models.ForeignKey(
        Bonus, on_delete=models.CASCADE, related_name='purchases')
    purchase_date = models.DateTimeField(default=timezone.now)
    date_begin = models.DateField(null=True, blank=True)
    date_end = models.DateField(null=True, blank=True)
    one_use_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - {self.bonus.get_bonus_type_display()} {self.bonus.activity} ({'Válido' if self.is_valid else 'No válido'})"

    @property
    def is_valid(self):
        date_now = timezone.now().date()
        type = self.bonus.bonus_type

        if type == 'single':
            return self.one_use_available
        elif type in ['annual', 'semester']:
            return self.date_begin and self.date_end and self.date_begin <= date_now <= self.date_end
        return False

    def use_single_use(self):
        """Sets the single use bonus to used"""
        if self.bonus.bonus_type == 'single':
            self.one_use_available = False
            self.save()

    def cancel_single_use(self):
        """Cancels a single bonus"""
        if self.bonus.bonus_type == 'single':
            self.one_use_available = True
            self.save()

    def belongs_to_activity(self, activity):
        """Verifies if the bonus belongs to an activity"""
        return self.bonus.activity == activity


class WaitingList(models.Model):
    """Class representing the waiting list for a full session"""
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='waiting_lists')
    session = models.ForeignKey(
        'src.Session', on_delete=models.CASCADE, related_name='waiting_list')
    join_date = models.DateTimeField(default=timezone.now)
    notified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'session')
        ordering = ['join_date']

    def __str__(self):
        return f"{self.user.username} se encuentra en la lista de espera para la sesión {self.session}"
