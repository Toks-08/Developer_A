from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegistrationView, LoginView,LogoutView,VerifyOTPView,PasswordResetView

urlpatterns = [
    path("register/", RegistrationView.as_view(), name='register' ),
    path('login/', LoginView.as_view(), name ="login"),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('verify/', VerifyOTPView.as_view(), name='verify-otp'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('reset-password/', PasswordResetView.as_view(), name='reset-password'),
    ]