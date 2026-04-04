from django.db import models

class Team(models.Model):
    name = models.CharField(max_length=255)
    project_name = models.CharField(max_length=255)

    def __str__(self):
        return self.name