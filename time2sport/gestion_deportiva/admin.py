from django.contrib import admin
from .models import SportFacility, Activity, Schedule, Photo
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserChangeForm
from .models import User

# Register your models here.
admin.site.register(SportFacility)
admin.site.register(Activity)
admin.site.register(Schedule)
admin.site.register(Photo)

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = '__all__'

    def clean_password(self):
        """Evita que Django requiera una contraseña."""
        return self.initial.get('password')

class UserAdmin(BaseUserAdmin):
    form = CustomUserChangeForm  

    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)

    fieldsets = (
        (None, {'fields': ('username', 'email', 'id')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'profile','is_uam','user_type')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:  
            return ('password', 'id')
        return super().get_readonly_fields(request, obj)

admin.site.register(User, UserAdmin)