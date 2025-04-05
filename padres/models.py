from django.db import models
from core.models import BaseModel
from cloudinary.models import CloudinaryField
import uuid

# Create your models here.
class Padre(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    firstName = models.CharField(max_length=100)
    lastName = models.CharField(max_length=100)
    birthDate = models.DateField()
    picture = CloudinaryField('image', blank=True, null=True)
    email = models.EmailField(null=True, blank=True)
    facebook = models.URLField(null=True, blank=True)
    twitter = models.URLField(null=True, blank=True)
    instagram = models.URLField(null=True, blank=True)

    def __str__(self):
        return f"{self.firstName} {self.lastName}"
