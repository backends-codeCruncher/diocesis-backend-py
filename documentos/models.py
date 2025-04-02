from django.db import models
from core.models import BaseModel
from django.conf import settings
from cloudinary.models import CloudinaryField

DOCUMENT_TYPE_CHOICES = [
    ("carta", "Carta"),
    ("circular", "Circular"),
    ("comunicado", "Comunicado"),
    ("prensa", "Prensa"),
    ("decreto", "Decreto"),
    ("instruccion", "Instrucción"),
    ("mensaje", "Mensaje"),
    ("dominical", "Dominical"),
    ("rescripto", "Rescripto"),
]

class Documento(BaseModel):
    title = models.CharField(max_length=255)
    document = CloudinaryField('file')
    type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES)
    tags = models.JSONField(default=list, blank=True)
    createdBy = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="documentos_creados"
    )

    def __str__(self):
        return self.title
    
    