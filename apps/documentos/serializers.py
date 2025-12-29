from rest_framework import serializers
from apps.documentos.models import Documento

class DocumentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Documento
        fields = '__all__'
        read_only_fields = (
            'id', 'isActive', 'createdAt', 'updatedAt', 'deletedAt',
            'updatedBy', 'deletedBy'
        )

