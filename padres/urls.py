from django.urls import path
from padres.views import PadreView

urlpatterns = [
    path('', PadreView.as_view(), name='padre_list_create'),
    path('<uuid:pk>/', PadreView.as_view(), name='padre_detail'),
]