from django.db import models
from django.conf import settings
import uuid

class Carrusel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    url = models.URLField()  # Se guarda como URL (subido manualmente a Cloudinary)
    isImage = models.BooleanField(default=True)
    isActive = models.BooleanField(default=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    createdBy = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='carruseles_creados'
    )

    def __str__(self):
        return f"{'Imagen' if self.isImage else 'Video'} - {self.id}"