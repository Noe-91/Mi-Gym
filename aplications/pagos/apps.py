from django.apps import AppConfig


class PagosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'aplications.pagos'

    def ready(self):
        # Import signals to ensure they are registered when the app is ready
        try:
            from . import signals  # noqa: F401
        except Exception:
            # avoid breaking startup if signals fail to import
            pass
