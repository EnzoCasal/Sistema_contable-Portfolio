from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ("admin", "Admin"),
        ("contador", "Contador"),
        ("auxcontable", "Auxiliar contable"),
        ("auditor", "Auditor"),
    )
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default="usuario")