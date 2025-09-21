from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ("admin", "Admin"),
        ("contador", "Contador"),
        ("auditor", "Auditor"),
    )
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default="auditor")
    dado_baja = models.BooleanField(default=False)