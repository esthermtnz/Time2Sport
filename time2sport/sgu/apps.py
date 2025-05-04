from django.apps import AppConfig


class SguConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sgu'

    def ready(self):
        import sgu.signals
