from django.shortcuts import render
from .serializers import (RegisterSerializer, LoginSerializer, VerifyOTPSerializer,
                          PasswordResetSerializer, ForgotPasswordResetSerializer, SendOTPSerializer)
from .models import CustomUser, EmailOTP
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
import random
from django.conf import settings

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
        
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        old_password = serializer.validated_data['old_password']
        new_password = serializer.validated_data['new_password']

        if not user.check_password(old_password):
            return Response({"error": "Old password is incorrect."}, status=400)
        

        user.set_password(new_password)
        user.save()

        return Response({"message": "Password changed successfully!"}, status=200)
    

class ForgotPasswordResetView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ForgotPasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        otp_code = serializer.validated_data['otp']
        new_password = serializer.validated_data['new_password']

        try:
            user = CustomUser.objects.get(email=email)

            otp_obj = EmailOTP.objects.filter(
                user=user,
                otp=otp_code,
                is_verified=False
            ).order_by('-created_at').first()
            

            if not otp_obj:
                return Response({"error": "Invalid OTP"}, status=400)

            if otp_obj.is_expired():
                return Response({"error": "OTP expired"}, status=400)

            
            user.set_password(new_password)
            user.save()

            otp_obj.is_verified = True
            otp_obj.save()

            return Response({"message": "Password reset successful"})

        except CustomUser.DoesNotExist:
            return Response({"error": "Invalid credentials"}, status=400)
        
        
class SendOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']

        try:
            user = CustomUser.objects.get(email=email)

            EmailOTP.objects.filter(user=user, is_verified=False).update(is_verified=True)

            otp = str(random.randint(100000, 999999))
            EmailOTP.objects.create(user=user, otp=otp,
                expires_at=timezone.now() + timedelta(minutes=10))

            if settings.DEBUG:
                return Response({
                    "message": "OTP sent successfully",
                    "otp": otp,
                    
                })

        except CustomUser.DoesNotExist:
            pass

        return Response({"message": "If the email exists, OTP has been sent"})