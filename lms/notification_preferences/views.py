from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from .models import UserNotificationPreference
from .serializers import NotificationPreferenceSerializer

class NotificationPreferenceView(RetrieveUpdateAPIView):
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        prefs, _ = UserNotificationPreference.objects.get_or_create(user=self.request.user)
        return prefs