from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import CustomUser, EmailOTP
from django.contrib.auth import authenticate
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
import random

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = CustomUser
        fields = [ "email","first_name","last_name", "phone_number","role","discipline","password", "password2"]

    def validate(self, attrs):
        if attrs ['password'] != attrs['password2']:
            raise serializers.ValidationError ("Passswords Do Not Match")
        return attrs

    def create(self, validated_data):
        #Pop the raw string and the extra password
        validated_data.pop("password2")
        
        password = validated_data.pop("password")
        
        #Create the user
        user = CustomUser.objects.create_user(password=password, **validated_data)
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
            otp_obj = EmailOTP.objects.filter(user=user, otp=otp_code).latest('created_at')

            if otp_obj.is_verified:
                raise serializers.ValidationError("This OTP has already been used.")

            if otp_obj.is_expired():
                raise serializers.ValidationError("This OTP has expired. Please request a new one.")

            if otp_obj.attempts >= 5:
                raise serializers.ValidationError("Too many failed attempts. Request a new code.")

            data['otp_instance'] = otp_obj
            data['user'] = user
            return data

        except (CustomUser.DoesNotExist, EmailOTP.DoesNotExist):
            raise serializers.ValidationError("Invalid email or OTP code.")
        

class PasswordResetSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({"error": "Passwords do not match."})
        data.pop('confirm_password')
        
        return data
    

class RequestPasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email does not exist.")
        return value

    def save(self):
        user = CustomUser.objects.get(email=self.validated_data['email'])

        uid = urlsafe_base64_encode(force_bytes(user.id))
        token = PasswordResetTokenGenerator().make_token(user)

        reset_link = f"http://localhost:3000/reset-password/{uid}/{token}/"

        send_mail(
            subject="Reset Your Password",
            message=f"Click the link to reset your password:\n{reset_link}",
            from_email="your_email@gmail.com",
            recipient_list=[user.email],
        )    

class ResetPasswordSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        # Check passwords match
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")

        # Decode user
        try:
            user_id = urlsafe_base64_decode(data['uid']).decode()
            user = CustomUser.objects.get(id=user_id)
        except:
            raise serializers.ValidationError("Invalid UID")

        # Validate token
        if not PasswordResetTokenGenerator().check_token(user, data['token']):
            raise serializers.ValidationError("Invalid or expired token")

        data['user'] = user
        return data

    def save(self):
        user = self.validated_data['user']
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user

class SendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()


class RequestEmailChangeSerializer(serializers.Serializer):
    new_email = serializers.EmailField()
    current_password = serializers.CharField(write_only=True)

    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Incorrect password.")
        return value

    def validate_new_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email is already in use.")
        return value

    def save(self):
        user = self.context['request'].user
        new_email = self.validated_data['new_email']

        otp_code = str(random.randit(100000, 999999))
        EmailOTP.objects.create(
            user=user,
            otp=otp_code,
            expires_at=timezone.now() + timedelta(minutes=10)
        )

        # TODO: Send OTP to the new email
        print(f"Send this OTP to {new_email}: {otp_code}")  # Replace with email sending logic

        return user
    
class VerifyEmailChangeOTPSerializer(serializers.Serializer):
    new_email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

    def validate(self, data):
        new_email = data['new_email']
        otp_code = data['otp']
        user = self.context['request'].user

        try:
            otp_obj = EmailOTP.objects.filter(user=user, otp=otp_code).latest('created_at')

            if otp_obj.is_verified:
                raise serializers.ValidationError("This OTP has already been used.")
            if otp_obj.is_expired():
                raise serializers.ValidationError("OTP expired. Request a new one.")

            data['otp_instance'] = otp_obj
            return data
        except EmailOTP.DoesNotExist:
            raise serializers.ValidationError("Invalid OTP.")

    def save(self):
        user = self.context['request'].user
        new_email = self.validated_data['new_email']
        otp_obj = self.validated_data['otp_instance']

        user.email = new_email
        user.is_email_verified = True
        user.save()

        otp_obj.is_verified = True
        otp_obj.save()
        return user