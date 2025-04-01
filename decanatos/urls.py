from django.urls import path
from .views import DecanatoView, CargarDecanatosPorCSV, HabilitarDecanatoView

urlpatterns = [
    path('', DecanatoView.as_view(), name='decanatos'),
    path('<uuid:pk>/', DecanatoView.as_view(), name='decanato-detalle'),
    path('cargar-csv/', CargarDecanatosPorCSV.as_view(), name='decanatos-cargar-csv'),
    path('habilitar/<uuid:pk>/', HabilitarDecanatoView.as_view(), name='decanato-habilitar'),
]