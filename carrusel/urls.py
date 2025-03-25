from django.urls import path
from .views import CarruselView

urlpatterns = [
    path('', CarruselView.as_view(), name='carrusel_list_create'),
    path('<uuid:pk>/', CarruselView.as_view(), name='carrusel_detail'),
]

