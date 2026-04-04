from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (RegistrationView, LoginView,LogoutView,VerifyOTPView,
                    ChangePasswordView, RequestPasswordResetView,ResetPasswordView, SendOTPView,
                    RequestEmailChangeView, VerifyEmailChangeOTPView)

urlpatterns = [
    path("auth/signup/", RegistrationView.as_view(), name='register' ),
    path('auth/login/', LoginView.as_view(), name ="login"),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/verify-email/', VerifyOTPView.as_view(), name='verify-otp'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/reset-password/', ChangePasswordView.as_view(), name='reset-password'),
    path('auth/resend-verification/', SendOTPView.as_view(), name='send-otp'),
    path('auth/forgot-password-reset/', RequestPasswordResetView.as_view()),
    path('auth/forgot-password-confirm/', ResetPasswordView.as_view()),
    path('settings/change-email/request/', RequestEmailChangeView.as_view(), name='request-change-email'),
    path('settings/change-email/confirm/', VerifyEmailChangeOTPView.as_view(), name='confirm-change-email'),
    ]