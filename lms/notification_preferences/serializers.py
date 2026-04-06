from rest_framework import serializers
from .models import UserNotificationPreference

class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserNotificationPreference
        fields = [
            'assignment_reminder',
            'announcements',
            'team_chat_mentions',
            'email_notifications',
        ]