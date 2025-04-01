from django.urls import path
from parroquias.views import ParroquiaView, HabilitarParroquiaView, CargarParroquiasPorCSV

urlpatterns = [
    path('', ParroquiaView.as_view(), name='parroquias'),
    path('<uuid:pk>/', ParroquiaView.as_view(), name='parroquia-detalle'),
    path('habilitar/<uuid:pk>/', HabilitarParroquiaView.as_view(), name='parroquia-habilitar'),
    path('cargar-csv/', CargarParroquiasPorCSV.as_view(), name='parroquias-cargar-csv'),
]