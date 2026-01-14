from rest_framework import serializers
from apps.documentos.models import Documento
import json

class DocumentoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Documento
        fields = '__all__'
        read_only_fields = (
            'id', 'isActive', 'createdAt', 'updatedAt', 'deletedAt',
            'updatedBy', 'deletedBy'
        )

    def validate_tags(self, value):
        """
        Siempre convierte tags a JSON real
        """
        if value in ("", None, "null"):
            return []

        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                raise serializers.ValidationError("Value must be valid JSON.")

        return value

