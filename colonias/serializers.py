from rest_framework import serializers
from colonias.models import Colonia

class ColoniaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Colonia
        fields = '__all__'
        read_only_fields = (
            'id', 'isActive', 'createdAt', 'updatedAt', 'deletedAt', 'updatedBy', 'deletedBy'
        )

        