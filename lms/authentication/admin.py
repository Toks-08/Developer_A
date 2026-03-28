from django.contrib import admin
from .models import CustomUser,EmailOTP

# Use the built-in UserAdmin logic so passwords work correctly
admin.site.register(CustomUser) 
admin.site.register(EmailOTP)