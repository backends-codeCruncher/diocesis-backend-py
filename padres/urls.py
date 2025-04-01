from django.urls import path
from padres.views import PadreView, CargarPadresPorCSV, HabilitarPadreView

urlpatterns = [
    path('', PadreView.as_view(), name='padre_list_create'),
    path('<uuid:pk>/', PadreView.as_view(), name='padre_detail'),
    path('habilitar/<uuid:pk>/', HabilitarPadreView.as_view(), name='padre_habilitar'),
    path('cargar-por-csv/', CargarPadresPorCSV.as_view(), name='padre_csv'),
]