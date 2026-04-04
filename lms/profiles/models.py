from django.db import models
from authentication.models import CustomUser

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True)
    tech_stack = models.CharField(max_length=255, blank=True, help_text="e.g. Python, Django, React")
    github_link = models.URLField(max_length=200, blank=True)
    linkedin_link = models.URLField(max_length=200, blank=True)
    profile_picture = models.ImageField(upload_to='avatars/', default='avatars/default.png', blank=True)
    
    is_profile_complete = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.full_name}'s Profile"