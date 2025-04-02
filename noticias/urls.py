from django.urls import path
from noticias.views import NoticiaView, HabilitarNoticiaView

urlpatterns = [
    path('', NoticiaView.as_view(), name='noticias'),
    path('<uuid:pk>/', NoticiaView.as_view(), name='noticia-detalle'),
    path('habilitar/<uuid:pk>/', HabilitarNoticiaView.as_view(), name='noticia-habilitar'),
]

