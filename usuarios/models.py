from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from core.models import BaseModel

ROLE_CHOICES = (
    ('super', 'Superusuario'),
    ('admin', 'Administrador'),
    ('user', 'Usuario'),
)

class UsuarioManager(BaseUserManager):
    def create_user(self, username, email, password=None, role='user', **extra_fields):
        email = self.normalize_email(email)

        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('isActive', True)

        user = self.model(username=username, email=email, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('role', 'super')
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('isActive', True)
        return self.create_user(username, email, password, **extra_fields)

class Usuario(AbstractBaseUser, PermissionsMixin, BaseModel):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    is_staff = models.BooleanField(default=False)


    is_active = models.BooleanField(default=True)

    objects = UsuarioManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username
    
    