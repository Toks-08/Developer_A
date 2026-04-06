from authentication.models import CustomUser
from django.db import models

class UserNotificationPreference(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='notification_preferences')

    assignment_reminder = models.BooleanField(default=True)
    announcements = models.BooleanField(default=True)
    team_chat_mentions = models.BooleanField(default=True)
    email_notifications = models.BooleanField(default=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} Notification Preferences"