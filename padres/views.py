import csv
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from padres.models import Padre
from padres.serializers import PadreSerializer

from cloudinary.uploader import upload

class CustomPageNumberPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class PadreView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request, pk=None):
        if pk:
            padre = get_object_or_404(Padre, pk=pk)
            serializer = PadreSerializer(padre)
            return Response(serializer.data)

        queryset = Padre.objects.all().order_by('-createdAt')

        first_name = request.query_params.get('firstName')
        last_name = request.query_params.get('lastName')

        if first_name:
            queryset = queryset.filter(firstName__icontains=first_name)
        if last_name:
            queryset = queryset.filter(lastName__icontains=last_name)

        paginator = CustomPageNumberPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = PadreSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        data = request.data.copy()

        picture_file = request.FILES.get('picture')
        if picture_file:
            resultado = upload(picture_file, folder="padres")
            data['picture'] = resultado.get('secure_url')

        serializer = PadreSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        padre = get_object_or_404(Padre, pk=pk) 
        data = request.data.copy()

        picture_file = request.FILES.get('picture')
        if picture_file:
            resultado = upload(picture_file, folder="padres")
            data['picture'] = resultado.get('secure_url')

        serializer = PadreSerializer(padre, data=data, partial=True)
        if serializer.is_valid():
            serializer.save(updatedBy=request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        padre = get_object_or_404(Padre, pk=pk)
        padre.isActive = False
        padre.deletedBy = request.user
        padre.save()
        return Response({"detail": "Padre desactivado correctamente."}, status=status.HTTP_204_NO_CONTENT)


class CargarPadresPorCSV(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser]

    def post(self, request):
        archivo = request.FILES.get('archivo_csv')
        if not archivo:
            return Response({"error": "No se proporcionó un archivo CSV."}, status=status.HTTP_400_BAD_REQUEST)

        reader = csv.DictReader(archivo.read().decode('utf-8').splitlines())
        creados = []
        errores = []

        for fila in reader:
            serializer = PadreSerializer(data=fila)
            if serializer.is_valid():
                serializer.save()
                creados.append(f"{fila.get('firstName')} {fila.get('lastName')}")
            else:
                errores.append({f"{fila.get('firstName')} {fila.get('lastName')}": serializer.errors})

        return Response({"creados": creados, "errores": errores}, status=status.HTTP_200_OK)