# authentication/serializers.py
from rest_framework import serializers
from .models import Profile
from authentication.models import CustomUser

class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    full_name = serializers.CharField(source='user.full_name', read_only=True)

    class Meta:
        model = Profile
        fields = ['email', 'full_name', 'bio', 'tech_stack', 'github_link', 'linkedin_link', 'avatar']

class LearnerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['bio', 'tech_stack', 'avatar', 'github_link']

class LearnerListSerializer(serializers.ModelSerializer):
    # This nesting allows you to see profile data inside the user object
    profile = LearnerProfileSerializer(read_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'full_name', 'email', 'role', 'date_joined', 'profile']


class InstructorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['bio', 'tech_stack', 'github_link', 'linkedin_link', 'avatar', 'is_profile_complete']

class InstructorUserSerializer(serializers.ModelSerializer):
    profile = InstructorProfileSerializer()

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'full_name', 'phone_number', 'role', 'profile']
        read_only_fields = ['email', 'role'] 

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', None)
        
        # Update User fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update Profile fields
        if profile_data:
            profile = instance.profile
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()
            
        return instance