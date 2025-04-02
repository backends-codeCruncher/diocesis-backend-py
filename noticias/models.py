from django.db import models
from core.models import BaseModel
from django.conf import settings
from cloudinary.models import CloudinaryField

class Noticia(BaseModel):
    title = models.CharField(max_length=255)
    picture = CloudinaryField('image', blank=True, null=True)
    content = models.TextField()
    tags = models.JSONField(default=list, blank=True)
    createdBy = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        related_name='noticias_creadas',
        on_delete=models.SET_NULL
    )

    def __str__(self):
        return self.title
    
    