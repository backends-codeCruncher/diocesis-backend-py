from rest_framework import serializers
from apps.parroquias.models import Parroquia

class ParroquiaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parroquia
        fields = '__all__'
        read_only_fields = (
            'id', 'isActive', 'createdAt', 'updatedAt', 'deletedAt',
            'updatedBy', 'deletedBy'
        )

        


