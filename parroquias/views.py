import csv
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.parsers import  MultiPartParser, FormParser, JSONParser
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import get_object_or_404
from django.conf import settings
import cloudinary.uploader
from parroquias.models import Parroquia
from parroquias.serializers import ParroquiaSerializer
from cloudinary.uploader import upload

def es_admin_o_super(user):
    return user.is_authenticated and user.role in ['admin', 'super']

class CustomPageNumberPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class ParroquiaView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]
    
    
    def get(self, request, pk=None):
        if pk:
            parroquia = get_object_or_404(Parroquia, pk=pk)
            serializer = ParroquiaSerializer(parroquia)
            return Response(serializer.data)

        queryset = Parroquia.objects.all().order_by('-createdAt')
        name = request.query_params.get('name')
        colonia = request.query_params.get('colonia')
        town = request.query_params.get('town')

        if name:
            queryset = queryset.filter(name__icontains=name)
        if colonia:
            queryset = queryset.filter(coloniaId__nombre__icontains=colonia)
        if town:
            queryset = queryset.filter(town__icontains=town)

        paginator = CustomPageNumberPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = ParroquiaSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        if not es_admin_o_super(request.user):
            return Response({"detail": "No autorizado."}, status=403)

        data = request.data.copy()
        picture_file = request.FILES.get('picture')
        if picture_file:
            cloudinary.config(
                cloud_name=settings.CLOUDINARY_STORAGE['CLOUD_NAME'],
                api_key=settings.CLOUDINARY_STORAGE['API_KEY'],
                api_secret=settings.CLOUDINARY_STORAGE['API_SECRET'],
                secure=True
            )
            resultado = upload(picture_file, folder="parroquia")
            data['picture'] = resultado.get('secure_url')

        serializer = ParroquiaSerializer(data=data)
        if serializer.is_valid():
            serializer.save(createdBy=request.user, isActive=True)
            return Response(serializer.data, status=201)
        
        return Response(serializer.errors, status=400)

    def put(self, request, pk):
        if not es_admin_o_super(request.user):
            return Response({"detail": "No autorizado."}, status=status.HTTP_403_FORBIDDEN)
        if not pk:
                return Response({"error": "Se requiere el ID de la parroquia."}, status=400)

        parroquia = get_object_or_404(Parroquia, pk=pk)
        data = request.data.copy()

        # 📷 Subida de nueva imagen (si viene)
        picture_file = request.FILES.get('picture')
        if picture_file:
            cloudinary.config(
                cloud_name=settings.CLOUDINARY_STORAGE['CLOUD_NAME'],
                api_key=settings.CLOUDINARY_STORAGE['API_KEY'],
                api_secret=settings.CLOUDINARY_STORAGE['API_SECRET'],
                secure=True
            )
            resultado = upload(picture_file, folder="parroquia")
            data['picture'] = resultado.get('secure_url')

        serializer = ParroquiaSerializer(parroquia, data=data, partial=True)
        if serializer.is_valid():
            serializer.save(updatedBy=request.user)
            return Response(serializer.data, status=200)
        
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        if not es_admin_o_super(request.user):
            return Response({"detail": "No autorizado."}, status=status.HTTP_403_FORBIDDEN)

        parroquia = get_object_or_404(Parroquia, pk=pk)
        parroquia.isActive = False
        parroquia.deletedBy = request.user
        parroquia.save()
        return Response({"detail": "Parroquia desactivada correctamente."}, status=status.HTTP_204_NO_CONTENT)

class HabilitarParroquiaView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        if not es_admin_o_super(request.user):
            return Response({"detail": "No autorizado."}, status=status.HTTP_403_FORBIDDEN)

        parroquia = get_object_or_404(Parroquia, pk=pk, isActive=False)
        parroquia.isActive = True
        parroquia.updatedBy = request.user
        parroquia.save()
        return Response({"detail": "Parroquia habilitada correctamente."}, status=status.HTTP_200_OK)

class CargarParroquiasPorCSV(APIView):
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
            serializer = ParroquiaSerializer(data=fila)
            if serializer.is_valid():
                serializer.save(createdBy=request.user)
                creados.append(fila.get('name'))
            else:
                errores.append({fila.get('name'): serializer.errors})

        return Response({"creados": creados, "errores": errores}, status=status.HTTP_200_OK)
    
