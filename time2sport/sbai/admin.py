from django.contrib import admin
from .models import SportFacility, Activity, Schedule, Photo, Bonus

admin.site.register(SportFacility)
admin.site.register(Activity)
admin.site.register(Schedule)
admin.site.register(Photo)
admin.site.register(Bonus)
