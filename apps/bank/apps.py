from django.apps import AppConfig


class BankConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.bank'
    
    def ready(self):
        import apps.bank.signals  # noqa
