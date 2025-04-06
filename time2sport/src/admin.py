from django.contrib import admin

from .models import Reservation, Session
# Register your models here.

admin.site.register(Reservation)
admin.site.register(Session)
