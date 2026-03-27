from django.shortcuts import render
from .serializers import RegisterSerializer, LoginSerializer, VerifyOTPSerializer,PasswordResetSerializer,ProfileSerializer
from .models import CustomUser, EmailOTP, Profile
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
import random

# Create your views here.
class RegistrationView(CreateAPIView):
    model = CustomUser
    serializer_class = RegisterSerializer
    permission_classes=[AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate and Save OTP 
        otp_code = str(random.randint(100000, 999999))
        EmailOTP.objects.create(
            user=user,
            otp=otp_code,
            expires_at=timezone.now() + timedelta(minutes=10)
        )
        return Response(
            {"message": "Registration successful. Please check your email for the OTP."},
            status=status.HTTP_201_CREATED
        )
        
    
    # The view to handle account activation
class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        otp_obj = serializer.validated_data['otp_instance']

        # Activate the user
        user.is_active = True
        user.is_email_verified = True
        user.save()

        # Mark OTP as used
        otp_obj.is_verified = True
        otp_obj.save()

        return Response({"Message": "Account activated! You can now login."}, status=status.HTTP_200_OK)

class LoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "message": "Login Successful",
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    'id': user.id,
                    'email': user.email,
                    'role': user.role,
                }
            }, 
            status=status.HTTP_200_OK
        )
    

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist() # This adds the token to the "banned" list
            return Response({"message": "Successfully logged out."}, status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response({"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)
        
class PasswordResetView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        otp_code = serializer.validated_data['otp']
        new_password = serializer.validated_data['new_password']

        try:
            user = CustomUser.objects.get(email=email)
            otp_obj = EmailOTP.objects.filter(user=user, otp=otp_code, is_verified=False).latest('created_at')

            if otp_obj.is_expired():
                return Response({"error": "OTP expired."}, status=status.HTTP_400_BAD_REQUEST)

            # Update Password
            user.set_password(new_password)
            user.save()

            # Mark OTP as used
            otp_obj.is_verified = True
            otp_obj.save()

            return Response({"message": "Password reset successful!"}, status=status.HTTP_200_OK)

        except (CustomUser.DoesNotExist, EmailOTP.DoesNotExist):
            return Response({"error": "Invalid Email or OTP."}, status=status.HTTP_400_BAD_REQUEST)
        
class ProfileDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = request.user.profile
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

    def patch(self, request):
        profile = request.user.profile
        # 'partial=True' allows updating just one field (like just the bio)
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            
            # Logic to auto-complete profile status
            if profile.bio and profile.tech_stack:
                profile.is_profile_complete = True
                profile.save()
                
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)