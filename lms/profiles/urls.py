from .views import LearnerListView, InstructorProfileView, ProfileDetailView
from django.urls import path

urlpatterns = [
    path('interns/', LearnerListView.as_view(), name='interns'),
    path('instructor/me/', InstructorProfileView.as_view(), name='instructor_me'),
    path('users/me/', ProfileDetailView.as_view(), name= 'profile')

]