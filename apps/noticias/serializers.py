from rest_framework import serializers
from apps.noticias.models import Noticia

class NoticiaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Noticia
        fields = '__all__'
        read_only_fields = (
            'id', 'isActive', 'createdAt', 'updatedAt', 'deletedAt',
            'updatedBy', 'deletedBy'
        )

        