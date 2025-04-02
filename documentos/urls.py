from django.urls import path
from documentos.views import DocumentoView, HabilitarDocumentoView

urlpatterns = [
    path('', DocumentoView.as_view(), name='documentos'),
    path('<uuid:pk>/', DocumentoView.as_view(), name='documento-detalle'),
    path('habilitar/<uuid:pk>/', HabilitarDocumentoView.as_view(), name='documento-habilitar'),
]

