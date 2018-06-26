from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender='api.User')
def save_user(sender, instance,update_fields, **kwargs):
   pass