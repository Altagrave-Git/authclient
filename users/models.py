from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    access_token = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255, blank=True, null=True)
    token_type = models.CharField(max_length=255)
    expires_in = models.IntegerField(default=0)
    expires_at = models.DateTimeField(blank=True, null=True)
    scope = models.CharField(max_length=255)

    sub = models.IntegerField(unique=True, null=True, blank=True)
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(blank=True, null=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255,  blank=True, null=True)