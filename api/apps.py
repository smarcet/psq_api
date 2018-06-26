from django.apps import AppConfig
from django.db.models.signals import post_save
from .signals.users import save_user


class ApiConfig(AppConfig):
    name = 'api'
    verbose_name = "Api PSQ"

    def ready(self):
        post_save.connect(save_user, sender='api.User')