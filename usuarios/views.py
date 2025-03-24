import csv
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from .models import Usuario
from .serializers import UsuarioSerializer

# 🔹 Permiso común
def es_admin_o_super(user):
    return user.role in ['admin', 'super']

# 🔹 Paginación común
class CustomPageNumberPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

# 🔹 CRUD general
class UsuarioAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk=None):
        if pk:
            usuario = get_object_or_404(Usuario, pk=pk)
            serializer = UsuarioSerializer(usuario)
            return Response(serializer.data)

        if not es_admin_o_super(request.user):
            return Response({"detail": "No tienes permisos."}, status=403)

        queryset = Usuario.objects.exclude(id=request.user.id).order_by('username')
        username = request.query_params.get('username')
        is_active = request.query_params.get('isActive')

        if username:
            queryset = queryset.filter(username__icontains=username)
        if is_active is not None:
            queryset = queryset.filter(isActive=(is_active.lower() == 'true'))

        paginator = CustomPageNumberPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = UsuarioSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        if not es_admin_o_super(request.user):
            return Response({"detail": "No tienes permisos para crear usuarios."}, status=403)

        data = request.data
        if request.user.role == 'admin' and data.get('role') == 'super':
            return Response({"detail": "Un admin no puede crear usuarios con rol 'super'."}, status=403)

        if Usuario.objects.filter(username=data.get('username')).exists():
            return Response({"error": "El nombre de usuario ya está registrado."}, status=400)

        data['password'] = make_password(data.get('password'))
        serializer = UsuarioSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save(updatedBy=request.user)
            return Response({"mensaje": "Usuario creado correctamente", "data": serializer.data}, status=201)
        return Response(serializer.errors, status=400)

    def put(self, request, pk=None):
        if not pk:
            return Response({"error": "Se requiere el ID del usuario."}, status=400)

        usuario = get_object_or_404(Usuario, pk=pk)
        if request.user.role == 'admin' and usuario.role == 'super':
            return Response({"detail": "No puedes editar a un usuario con rol 'super'."}, status=403)

        serializer = UsuarioSerializer(usuario, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save(updatedBy=request.user)
            return Response({"mensaje": "Usuario actualizado correctamente", "data": serializer.data})
        return Response(serializer.errors, status=400)

    def delete(self, request, pk=None):
        if not pk:
            return Response({"error": "Se requiere el ID del usuario."}, status=400)

        usuario = get_object_or_404(Usuario, pk=pk)
        if request.user.role == 'admin' and usuario.role == 'super':
            return Response({"detail": "No puedes eliminar a un superusuario."}, status=403)

        usuario.isActive = False
        usuario.deletedAt = timezone.now()
        usuario.deletedBy = request.user
        usuario.save()
        return Response({"mensaje": "Usuario eliminado correctamente."}, status=200)


# 🔹 Activar/Desactivar usuario
class HabilitarUsuarioView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, pk=None):
        if not pk:
            return Response({"error": "Se requiere el ID del usuario."}, status=400)

        usuario = get_object_or_404(Usuario, pk=pk)

        if not es_admin_o_super(request.user):
            return Response({"error": "No tienes permisos para esto."}, status=403)

        if usuario.role == 'super' and request.user.role == 'admin':
            return Response({"error": "No puedes modificar el estado de un superusuario."}, status=403)

        usuario.isActive = not usuario.isActive
        usuario.updatedBy = request.user
        usuario.deletedBy = request.user if not usuario.isActive else None
        usuario.deletedAt = timezone.now() if not usuario.isActive else None
        usuario.save()

        estado = "activado" if usuario.isActive else "desactivado"
        return Response({"mensaje": f"Usuario {usuario.username} ha sido {estado} correctamente."})


# 🔹 Cambiar contraseña (solo usuario autenticado)
class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request):
        new_password = request.data.get("new_password")
        if not new_password:
            return Response({"error": "El campo 'new_password' es obligatorio."}, status=400)

        usuario = request.user
        usuario.password = make_password(new_password)
        usuario.save()

        return Response({"mensaje": "Contraseña actualizada correctamente."}, status=200)


# 🔹 Resetear contraseña (admin o super)
class ResetPasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk=None):
        if not pk:
            return Response({"error": "Se requiere el ID del usuario."}, status=400)

        if not es_admin_o_super(request.user):
            return Response({"error": "No tienes permisos para resetear contraseñas."}, status=403)

        usuario = get_object_or_404(Usuario, pk=pk)

        if request.user.role == 'admin' and usuario.role == 'super':
            return Response({"error": "Un admin no puede resetear la contraseña de un super."}, status=403)

        nueva_password = usuario.username
        usuario.password = make_password(nueva_password)
        usuario.save()

        return Response({"mensaje": f"Contraseña de {usuario.username} reseteada correctamente."}, status=200)


# 🔹 Ver perfil del usuario autenticado
class UsuarioPerfilView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UsuarioSerializer(request.user)
        return Response(serializer.data)


# 🔹 Crear usuarios por CSV
class CrearUsuariosPorCsvView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        archivo_csv = request.FILES.get('archivo_csv')
        if not archivo_csv:
            return Response({"error": "No se proporcionó un archivo CSV."}, status=400)

        if not es_admin_o_super(request.user):
            return Response({"error": "No tienes permisos para cargar CSV."}, status=403)

        decoded_file = archivo_csv.read().decode('utf-8').splitlines()
        reader = csv.DictReader(decoded_file)

        usuarios_creados = []
        errores = []

        for fila in reader:
            username = fila.get('username')
            email = fila.get('email')
            role = fila.get('role')
            password = fila.get('password') or username

            if not username or not email or not role:
                errores.append(f"Faltan campos obligatorios en la fila: {fila}")
                continue

            if role not in ['user', 'admin', 'super']:
                errores.append(f"Rol inválido para {username}")
                continue

            if request.user.role == 'admin' and role == 'super':
                errores.append(f"No puedes crear superusuarios como admin: {username}")
                continue

            if Usuario.objects.filter(username=username).exists():
                errores.append(f"Usuario ya existe: {username}")
                continue

            try:
                user = Usuario.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    role=role
                )
                user.updatedBy = request.user
                user.save()
                usuarios_creados.append(username)
            except Exception as e:
                errores.append(f"Error al crear {username}: {str(e)}")

        return Response({
            "mensaje": f"Se procesaron {len(usuarios_creados)} usuarios.",
            "creados": usuarios_creados,
            "errores": errores
        }, status=200)
    
