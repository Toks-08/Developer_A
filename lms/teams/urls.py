from django.urls import path
from .views import MyTeamView

urlpatterns = [
    path('my-team/', MyTeamView.as_view(), name='my-team'),
]