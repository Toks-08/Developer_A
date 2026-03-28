# authentication/views.py
from rest_framework import generics, filters, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from authentication.models import CustomUser
from .serializers import LearnerListSerializer,InstructorUserSerializer, ProfileSerializer

from rest_framework.exceptions import PermissionDenied

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

    # 1. Only fetch users who are INTERNS
    def get_queryset(self):
        return CustomUser.objects.filter(role=CustomUser.Role.INTERN).select_related('profile')

    # 2. Add Search and Ordering capabilities
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    
    # This allows you to search by name or tech stack (from the related profile)
    search_fields = ['full_name', 'email', 'profile__tech_stack']
    
    # This allows you to sort by newest joiners
    ordering_fields = ['date_joined', 'full_name']
    ordering = ['-date_joined'] # Default to newest first


class InstructorProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = InstructorUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        user = self.request.user
        
        if user.role == "INSTRUCTOR": 
            return user 
    
        raise PermissionDenied("This page is reserved for instructors.")
        
        
        
        

