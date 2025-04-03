import csv
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.parsers import MultiPartParser
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import get_object_or_404
from colonias.models import Colonia
from colonias.serializers import ColoniaSerializer


# Función para verificar si el usuario es admin o super
def es_admin_o_super(user):
    return user.is_authenticated and user.role in ['admin', 'super']

class CustomPageNumberPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class ColoniaView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request, pk=None):
        if pk:
            colonia = get_object_or_404(Colonia, pk=pk, isActive=True)
            serializer = ColoniaSerializer(colonia)
            return Response(serializer.data)

        queryset = Colonia.objects.filter(isActive=True).order_by('-createdAt')

        # Filtro por nombre
        name = request.query_params.get('name')
        if name:
            queryset = queryset.filter(name__icontains=name)

        paginator = CustomPageNumberPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = ColoniaSerializer(queryset, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        if not es_admin_o_super(request.user):
            return Response({"detail": "No autorizado."}, status=status.HTTP_403_FORBIDDEN)

        serializer = ColoniaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(createdBy=request.user, isActive=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        if not es_admin_o_super(request.user):
            return Response({"detail": "No autorizado."}, status=status.HTTP_403_FORBIDDEN)

        colonia = get_object_or_404(Colonia, pk=pk, isActive=True)
        serializer = ColoniaSerializer(colonia, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(updatedBy=request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        if not es_admin_o_super(request.user):
            return Response({"detail": "No autorizado."}, status=status.HTTP_403_FORBIDDEN)

        colonia = get_object_or_404(Colonia, pk=pk, isActive=True)
        colonia.isActive = False
        colonia.deletedBy = request.user
        colonia.save()
        return Response({"detail": "Colobia desactivado correctamente."}, status=status.HTTP_204_NO_CONTENT)
    
class CargarColoniaPorCSV(APIView):
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
            serializer = ColoniaSerializer(data=fila)
            if serializer.is_valid():
                serializer.save(createdBy=request.user)
                creados.append(fila.get('name'))
            else:
                errores.append({fila.get('name'): serializer.errors})

        return Response({"creados": creados, "errores": errores}, status=status.HTTP_200_OK)
    
class HabilitarColoniaView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        if not es_admin_o_super(request.user):
            return Response({"detail": "No autorizado."}, status=status.HTTP_403_FORBIDDEN)

        colonia = get_object_or_404(Colonia, pk=pk, isActive=False)
        colonia.isActive = True
        colonia.updatedBy = request.user
        colonia.save()
        return Response({"detail": "Colonia habilitado correctamente."}, status=status.HTTP_200_OK)
    
    