from rest_framework import serializers
from .models import Padre

class PadreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Padre
        fields = '__all__'
        read_only_fields = ['id', 'isActive', 'createdAt', 'updatedAt', 'deletedAt', 'updatedBy', 'deletedBy']

