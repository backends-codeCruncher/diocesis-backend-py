from django.urls import path
from articulos.views import ArticuloView, HabilitarArticuloView

urlpatterns = [
    path('', ArticuloView.as_view(), name='articulos'),
    path('<uuid:pk>/', ArticuloView.as_view(), name='articulo-detalle'),
    path('habilitar/<uuid:pk>/', HabilitarArticuloView.as_view(), name='articulo-habilitar'),
]


