from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import CustomUser, EmailOTP, Profile
from django.contrib.auth import authenticate

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = CustomUser
        fields = [ "email","full_name","phone_number","password", "password2"]

    def validate(self, attrs):
        if attrs ['password'] != attrs['password2']:
            raise serializers.ValidationError ("Passswords Do Not Match")
        return attrs

    def create(self, validated_data):
        #Pop the raw string and the extra password
        password = validated_data.pop("password2")
        
        #Create the user
        user = CustomUser.objects.create_user(**validated_data)
        return user
   

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, validated_data):
        user = authenticate(**validated_data)
        if not user:
            raise serializers.ValidationError("Invalid Username Or Password")
        validated_data['user']=user
        return validated_data
    

class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6, min_length=6)

    def validate(self, data):
        email = data.get('email')
        otp_code = data.get('otp')

        try:
            user = CustomUser.objects.get(email=email)
            # Get the latest OTP for this user
            otp_obj = EmailOTP.objects.filter(user=user, otp=otp_code).latest('created_at')
            
            # Check 1: Is it already verified?
            if otp_obj.is_verified:
                raise serializers.ValidationError("This OTP has already been used.")

            # Check 2: Use model logic to check if it's expired
            if otp_obj.is_expired():
                raise serializers.ValidationError("This OTP has expired. Please request a new one.")

            # Check 3: Brute force protection
            if otp_obj.attempts >= 5:
                raise serializers.ValidationError("Too many failed attempts. Request a new code.")

            data['otp_instance'] = otp_obj
            data['user'] = user
            return data

        except (CustomUser.DoesNotExist, EmailOTP.DoesNotExist):
            raise serializers.ValidationError("Invalid email or OTP code.")
        

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])


class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    full_name = serializers.CharField(source='user.full_name', read_only=True)

    class Meta:
        model = Profile
        fields = ['email', 'full_name', 'bio', 'tech_stack', 'github_link', 'linkedin_link', 'avatar']