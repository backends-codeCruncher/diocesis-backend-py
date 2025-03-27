from django.urls import path
from padres.views import PadreView, CargarPadresPorCSV

urlpatterns = [
    path('', PadreView.as_view(), name='padre_list_create'),
    path('<uuid:pk>/', PadreView.as_view(), name='padre_detail'),
    path('cargar-por-csv/', CargarPadresPorCSV.as_view(), name='padre_csv'),
]