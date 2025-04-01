import csv
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from padres.models import Padre
from padres.serializers import PadreSerializer

class PadreView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_permissions(self):
        # 👇 Permite el acceso libre al GET
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]  # POST, PUT, DELETE requieren autenticación

    def get(self, request, pk=None):
        if pk:
            padre = get_object_or_404(Padre, pk=pk)
            serializer = PadreSerializer(padre)
            return Response(serializer.data)

        queryset = Padre.objects.all().order_by('lastName')

        # 🔍 Filtros
        first_name = request.query_params.get('firstName')
        last_name = request.query_params.get('lastName')

        if first_name:
            queryset = queryset.filter(firstName__icontains=first_name)
        if last_name:
            queryset = queryset.filter(lastName__icontains=last_name)

        serializer = PadreSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PadreSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def put(self, request, pk):
        padre = get_object_or_404(Padre, pk=pk)
        serializer = PadreSerializer(padre, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(updatedBy=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        padre = get_object_or_404(Padre, pk=pk)
        padre.isActive = False
        padre.deletedBy = request.user
        padre.save()
        return Response({"detail": "Padre desactivado correctamente."}, status=204)
    
class CargarPadresPorCSV(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]

    def post(self, request):
        archivo = request.FILES.get('archivo_csv')
        if not archivo:
            return Response({"error": "No se proporcionó un archivo CSV."}, status=400)

        files = request.FILES
        reader = csv.DictReader(archivo.read().decode('utf-8').splitlines())
        creados = []
        errores = []

        for fila in reader:
            try:
                identificador = fila.get('identifier')  # clave única
                first_name = fila.get('firstName')
                last_name = fila.get('lastName')
                birth_date = fila.get('birthDate')

                # Buscar imagen con nombre exacto del identificador
                imagen = files.get(identificador, None)

                padre = Padre.objects.create(
                    firstName=first_name,
                    lastName=last_name,
                    birthDate=birth_date,
                    picture=imagen  # puede ser None
                )
                creados.append(f"{first_name} {last_name}")
            except Exception as e:
                errores.append(str(e))

        return Response({
            "creados": creados,
            "errores": errores
        })
    