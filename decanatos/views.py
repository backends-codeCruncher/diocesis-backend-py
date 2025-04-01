import csv
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.parsers import MultiPartParser
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from decanatos.models import Decanato
from decanatos.serializers import DecanatoSerializer


# Función para verificar si el usuario es admin o super
def es_admin_o_super(user):
    return user.is_authenticated and user.role in ['admin', 'super']

class CustomPageNumberPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class DecanatoView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk=None):
        if pk:
            decanato = get_object_or_404(Decanato, pk=pk, isActive=True)
            serializer = DecanatoSerializer(decanato)
            return Response(serializer.data)

        queryset = Decanato.objects.filter(isActive=True).order_by('-createdAt')

        # Filtro por nombre
        name = request.query_params.get('name')
        if name:
            queryset = queryset.filter(name__icontains=name)

        paginator = CustomPageNumberPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = DecanatoSerializer(queryset, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        if not es_admin_o_super(request.user):
            return Response({"detail": "No autorizado."}, status=status.HTTP_403_FORBIDDEN)

        serializer = DecanatoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(createdBy=request.user, isActive=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        if not es_admin_o_super(request.user):
            return Response({"detail": "No autorizado."}, status=status.HTTP_403_FORBIDDEN)

        decanato = get_object_or_404(Decanato, pk=pk, isActive=True)
        serializer = DecanatoSerializer(decanato, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(updatedBy=request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        if not es_admin_o_super(request.user):
            return Response({"detail": "No autorizado."}, status=status.HTTP_403_FORBIDDEN)

        decanato = get_object_or_404(Decanato, pk=pk, isActive=True)
        decanato.isActive = False
        decanato.deletedBy = request.user
        decanato.save()
        return Response({"detail": "Decanato desactivado correctamente."}, status=status.HTTP_204_NO_CONTENT)
    
class CargarDecanatosPorCSV(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser]

    def post(self, request):
        if not es_admin_o_super(request.user):
            return Response({"detail": "No autorizado."}, status=status.HTTP_403_FORBIDDEN)

        archivo = request.FILES.get('archivo_csv')
        if not archivo:
            return Response({"error": "No se proporcionó un archivo CSV."}, status=status.HTTP_400_BAD_REQUEST)

        reader = csv.DictReader(archivo.read().decode('utf-8').splitlines())
        creados = []
        errores = []

        for fila in reader:
            serializer = DecanatoSerializer(data=fila)
            if serializer.is_valid():
                serializer.save(createdBy=request.user)
                creados.append(fila.get('name'))
            else:
                errores.append({fila.get('name'): serializer.errors})

        return Response({"creados": creados, "errores": errores}, status=status.HTTP_200_OK)
    
class HabilitarDecanatoView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        if not es_admin_o_super(request.user):
            return Response({"detail": "No autorizado."}, status=status.HTTP_403_FORBIDDEN)

        decanato = get_object_or_404(Decanato, pk=pk, isActive=False)
        decanato.isActive = True
        decanato.updatedBy = request.user
        decanato.save()
        return Response({"detail": "Decanato habilitado correctamente."}, status=status.HTTP_200_OK)
    
    
