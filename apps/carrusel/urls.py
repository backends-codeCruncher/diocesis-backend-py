from django.urls import path
from .views import CarruselView, HabilitarCarruselView

urlpatterns = [
    path('', CarruselView.as_view(), name='carrusel_list_create'),
    path('<uuid:pk>/', CarruselView.as_view(), name='carrusel_detail'),
    path('habilitar/<uuid:pk>/', HabilitarCarruselView.as_view(), name='carrusel_habilitar'),
]

