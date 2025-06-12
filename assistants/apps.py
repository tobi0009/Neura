from django.apps import AppConfig


class AssistantsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'assistants'

    def ready(self):
        import assistants.signals  # connects the signal when app is ready



