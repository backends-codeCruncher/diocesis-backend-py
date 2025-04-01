from django.db import models
from django.conf import settings
from core.models import BaseModel
import uuid
# Create your models here.

class Decanato(BaseModel):
    name = models.CharField(max_length=255)
    createdBy = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        related_name="decanatos_created_by",
        on_delete=models.SET_NULL
    )

    def __str__(self):
        return self.name

