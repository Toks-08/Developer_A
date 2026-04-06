from django.db.models.signals import post_save
from django.dispatch import receiver
from ..authentication import CustomUser
from .models import UserNotificationPreference


@receiver(post_save, sender=CustomUser)
def create_user_notification_preferences(sender, instance, created, **kwargs):
    if created:
        UserNotificationPreference.objects.create(user=instance)