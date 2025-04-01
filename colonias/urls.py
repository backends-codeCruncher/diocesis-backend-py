from django.urls import path
from colonias.views import ColoniaView, CargarColoniaPorCSV, HabilitarColoniaView

urlpatterns = [
    path('', ColoniaView.as_view(), name='colonias'),
    path('<uuid:pk>/', ColoniaView.as_view(), name='colonia-detalle'),
    path('cargar-csv/', CargarColoniaPorCSV.as_view(), name='colonias-cargar-csv'),
    path('habilitar/<uuid:pk>/', HabilitarColoniaView.as_view(), name='colonia-habilitar'),
]