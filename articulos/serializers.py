from rest_framework import serializers
from articulos.models import Articulo

class ArticuloSerializer(serializers.ModelSerializer):
    class Meta:
        model = Articulo
        fields = '__all__'
        read_only_fields = (
            'id', 'isActive', 'createdAt', 'updatedAt', 'deletedAt',
            'updatedBy', 'deletedBy'
        )

