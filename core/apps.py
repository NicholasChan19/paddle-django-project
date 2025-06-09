from django.apps import AppConfig

class PaddleConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'paddle'

    def ready(self):
        import core.signals

class CoreConfig(AppConfig):
    name = 'core'  # HARUS sesuai nama folder app
    default_auto_field = 'django.db.models.BigAutoField'

    def ready(self):
        import core.signals  # WAJIB ADA ini