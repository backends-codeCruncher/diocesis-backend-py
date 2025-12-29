from rest_framework import serializers
from .models import Usuario

class UsuarioSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    updatedBy = serializers.StringRelatedField(read_only=True)
    deletedBy = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'email', 'password', 'role',
            'isActive', 'createdAt', 'updatedAt', 'deletedAt',
            'updatedBy', 'deletedBy'
        ]
        read_only_fields = ['id', 'isActive', 'createdAt', 'updatedAt', 'deletedAt', 'updatedBy', 'deletedBy']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = Usuario.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        validated_data.pop('password', None)
        request = self.context.get('request')
        current_user = request.user if request else None

        if current_user and current_user.role == 'admin' and instance.role == 'super':
            raise serializers.ValidationError("No puedes modificar un usuario con rol 'super'.")

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
    
    