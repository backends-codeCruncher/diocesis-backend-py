from rest_framework import serializers
from decanatos.models import Decanato

class DecanatoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Decanato
        fields = '__all__'
        read_only_fields = (
            'id', 'isActive', 'createdAt', 'updatedAt', 'deletedAt', 'updatedBy', 'deletedBy'
        )

        