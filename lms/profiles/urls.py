from .views import LearnerListView, InstructorListView, ProfileDetailView
from django.urls import path

urlpatterns = [
    path('learners/', LearnerListView.as_view(), name='interns'),
    path('instructors/', InstructorListView.as_view(), name='instructor_me'),
    path('users/me/', ProfileDetailView.as_view(), name= 'profile')

]