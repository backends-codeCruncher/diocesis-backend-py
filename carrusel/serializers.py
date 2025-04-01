from rest_framework import serializers
from .models import Carrusel

class CarruselSerializer(serializers.ModelSerializer):
    class Meta:
        model = Carrusel
        fields = '__all__'
        read_only_fields = ['id', 'createdAt', 'createdBy', 'isActive']

        