from django.db import models
from core.models import BaseModel
from colonias.models import Colonia
from decanatos.models import Decanato
from padres.models import Padre
from usuarios.models import Usuario
from cloudinary.models import CloudinaryField
# Create your models here.

class Parroquia(BaseModel):
    name = models.CharField(max_length=255)
    openingDate = models.DateField()
    decanatoId = models.ForeignKey(Decanato, on_delete=models.PROTECT, related_name="parroquias")
    address = models.TextField()
    coloniaId = models.ForeignKey(Colonia, on_delete=models.PROTECT, related_name="parroquias")
    zipCode = models.CharField(max_length=10)
    town = models.CharField(max_length=100)
    createdBy = models.ForeignKey(Usuario, null=True, blank=True, on_delete=models.SET_NULL, related_name="parroquias_created_by")
    padreId = models.ForeignKey(Padre, on_delete=models.PROTECT, related_name="parroquias")


    picture = CloudinaryField('image', blank=True, null=True)

    def __str__(self):
        return self.name
