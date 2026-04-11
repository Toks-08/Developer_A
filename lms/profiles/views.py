# authentication/views.py
from rest_framework import generics, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from authentication.models import CustomUser
from .serializers import LearnerListSerializer,InstructorListSerializer, ProfileSerializer
from authentication.permissions import (IsAdmin,IsInstructor,IsLearner)


class ProfileDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = request.user.profile
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

    def patch(self, request):
        profile = request.user.profile
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            
            # Logic to auto-complete profile status
            if profile.bio and profile.tech_stack:
                profile.is_profile_complete = True
                profile.save()
                
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LearnerListView(generics.ListAPIView):
    serializer_class = LearnerListSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):

        return CustomUser.objects.filter(role=CustomUser.Role.LEARNER).select_related('profile')
    
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['full_name', 'email', 'profile__tech_stack']
    ordering_fields = ['date_joined', 'full_name']
    ordering = ['-date_joined']


class InstructorListView(generics.ListAPIView):
    serializer_class = InstructorListSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        return CustomUser.objects.filter(
            role=CustomUser.Role.INSTRUCTOR
        ).select_related('profile')

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['full_name', 'email', 'profile__tech_stack']
    ordering_fields = ['date_joined', 'full_name']
    ordering = ['-date_joined']        
        
