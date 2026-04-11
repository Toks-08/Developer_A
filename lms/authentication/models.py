from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.utils import timezone
from datetime import timedelta


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    team = models.ForeignKey(
        'teams.Team',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='members'
    )
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=20, blank=True, unique=True, null=True)

    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    is_email_verified = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
    
    @property
    def is_learner(self):
        return self.role == self.Role.LEARNER

    @property
    def is_instructor(self):
        return self.role == self.Role.INSTRUCTOR

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN

    class Role(models.TextChoices):
        LEARNER = "LEARNER", "Learner"
        INSTRUCTOR = "INSTRUCTOR", "Instructor"
        
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.LEARNER

    )

    class Discipline(models.TextChoices):
        BACKEND = "BACKEND", "Backend"
        FRONTEND_DEVELOPMENT = "FRONTEND_DEVELOPMENT", "Frontend Development"
        PRODUCT_MANAGEMENT = "PRODUCT_MANAGEMENT", "Product Management"
    

    discipline = models.CharField(
        max_length=20,
        choices=Discipline.choices,
    )

def get_default_expiry():
    return timezone.now() + timedelta(minutes=10)

class EmailOTP(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name='email_otps')
    otp = models.CharField(max_length=6)
    is_verified = models.BooleanField(default=False)
    expires_at = models.DateTimeField(get_default_expiry)
    attempts = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.expires_at
    
