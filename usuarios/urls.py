from django.urls import path
from usuarios.views import (
    UsuarioAPIView,
    HabilitarUsuarioView,
    ChangePasswordView,
    ResetPasswordView,
    UsuarioPerfilView,
    CrearUsuariosPorCsvView,
)

urlpatterns = [
    # CRUD general
    path('usuarios/', UsuarioAPIView.as_view(), name='usuarios_list_create'),
    path('usuarios/<uuid:pk>/', UsuarioAPIView.as_view(), name='usuarios_detail'),

    # Activar / desactivar usuario
    path('usuarios/cambiar-estado/<uuid:pk>/', HabilitarUsuarioView.as_view(), name='usuario_cambiar_estado'),

    # Cambiar contraseña del usuario autenticado
    path('usuarios/change-password/', ChangePasswordView.as_view(), name='usuario_change_password'),

    # Resetear contraseña (admin/super)
    path('usuarios/reset-password/<uuid:pk>/', ResetPasswordView.as_view(), name='usuario_reset_password'),

    # Ver perfil del usuario autenticado
    path('usuarios/me/', UsuarioPerfilView.as_view(), name='usuario_perfil'),

    # Crear usuarios desde archivo CSV
    path('usuarios/cargar-por-csv/', CrearUsuariosPorCsvView.as_view(), name='usuario_cargar_csv'),
]

