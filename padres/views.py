import csv
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from padres.models import Padre
from django.conf import settings
import cloudinary.uploader
from padres.serializers import PadreSerializer
from cloudinary.uploader import upload


def es_admin_o_super(user):
    return user.is_authenticated and user.role in ['admin', 'super']

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
        if not es_admin_o_super(request.user):
            return Response({"detail": "No autorizado."}, status=403)

        data = request.data.copy()
        picture_file = request.FILES.get('picture')

        if picture_file:
            try:
                # ✅ Configurar Cloudinary antes de usarlo
                cloudinary.config(
                    cloud_name=settings.CLOUDINARY_STORAGE['CLOUD_NAME'],
                    api_key=settings.CLOUDINARY_STORAGE['API_KEY'],
                    api_secret=settings.CLOUDINARY_STORAGE['API_SECRET'],
                    secure=True
                )

                resultado = upload(
                    picture_file,
                    folder="padres",
                    use_filename=True,
                    unique_filename=False
                )
                data['picture'] = resultado.get('secure_url')

            except Exception as e:
                return Response({"error": str(e)}, status=400)

        serializer = PadreSerializer(data=data)
        if serializer.is_valid():
            serializer.save(isActive=True)
            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)

    def put(self, request, pk):
        if not es_admin_o_super(request.user):
            return Response({"detail": "No autorizado."}, status=status.HTTP_403_FORBIDDEN)

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
        if not es_admin_o_super(request.user):
            return Response({"detail": "No autorizado."}, status=status.HTTP_403_FORBIDDEN)

        padre = get_object_or_404(Padre, pk=pk)
        padre.isActive = False
        padre.deletedBy = request.user
        padre.save()
        return Response({"detail": "Padre desactivado correctamente."}, status=status.HTTP_204_NO_CONTENT)


class CargarPadresPorCSV(APIView):
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
            serializer = PadreSerializer(data=fila)
            if serializer.is_valid():
                serializer.save()
                creados.append(f"{fila.get('firstName')} {fila.get('lastName')}")
            else:
                errores.append({f"{fila.get('firstName')} {fila.get('lastName')}": serializer.errors})

        return Response({"creados": creados, "errores": errores}, status=status.HTTP_200_OK)
    

class HabilitarPadreView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        if not es_admin_o_super(request.user):
            return Response({"detail": "No autorizado."}, status=status.HTTP_403_FORBIDDEN)

        padre = get_object_or_404(Padre, pk=pk, isActive=False)
        padre.isActive = True
        padre.updatedBy = request.user
        padre.save()
        return Response({"detail": "Padre habilitado correctamente."}, status=status.HTTP_200_OK)
    
    