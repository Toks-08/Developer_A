# authentication/serializers.py
from rest_framework import serializers
from .models import Profile
from authentication.models import CustomUser

class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name',read_only=True)
    last_name = serializers.CharField(source='user.last_name',read_only=True)
    phone_number = serializers.CharField(source='user.phone_number', required=False)

    class Meta:
        model = Profile
        fields = ['email', 'first_name','last_name','phone_number','bio', 'tech_stack', 'github_link', 'linkedin_link', 'profile_picture']

class LearnerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['bio', 'tech_stack', 'profile_picture', 'github_link']

class LearnerListSerializer(serializers.ModelSerializer):
    profile = LearnerProfileSerializer(read_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'full_name', 'email', 'role', 'date_joined', 'profile']


class InstructorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['bio', 'tech_stack', 'github_link', 'linkedin_link', 'profile_picture', 'is_profile_complete']

class InstructorListSerializer(serializers.ModelSerializer):
    profile = InstructorProfileSerializer(read_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'first_name','last_name', 'email', 'role', 'profile']
