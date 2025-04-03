import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.conf import settings
import cloudinary.uploader
from noticias.models import Noticia
from noticias.serializers import NoticiaSerializer
from cloudinary.uploader import upload

def es_admin_o_super(user):
    return user.is_authenticated and user.role in ['admin', 'super']

class CustomPageNumberPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class NoticiaView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request, pk=None):
        if pk:
            noticia = get_object_or_404(Noticia, pk=pk)
            serializer = NoticiaSerializer(noticia)
            return Response(serializer.data)

        queryset = Noticia.objects.filter(isActive=True).order_by('-createdAt')

        title = request.query_params.get('title')
        tag = request.query_params.get('tag')

        if title:
            queryset = queryset.filter(title__icontains=title)
        if tag:
            queryset = queryset.filter(tags__icontains=tag)

        paginator = CustomPageNumberPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = NoticiaSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        if not es_admin_o_super(request.user):
            return Response({"detail": "No autorizado."}, status=403)

        data = request.data.copy()
        picture_file = request.FILES.get('picture')

        if picture_file:
            try:
                cloudinary.config(
                    cloud_name=settings.CLOUDINARY_STORAGE['CLOUD_NAME'],
                    api_key=settings.CLOUDINARY_STORAGE['API_KEY'],
                    api_secret=settings.CLOUDINARY_STORAGE['API_SECRET'],
                    secure=True
                )

                resultado = upload(
                    picture_file,
                    folder="noticias",
                    use_filename=True,
                    unique_filename=False
                )
                data['picture'] = resultado.get('secure_url')
            except Exception as e:
                return Response({"error": str(e)}, status=400)

        serializer = NoticiaSerializer(data=data)
        if serializer.is_valid():
            serializer.save(createdBy=request.user, isActive=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def put(self, request, pk):
        if not es_admin_o_super(request.user):
            return Response({"detail": "No autorizado."}, status=403)

        noticia = get_object_or_404(Noticia, pk=pk)
        data = request.data.copy()

        picture_file = request.FILES.get('picture')
        if picture_file:
            try:
                cloudinary.config(
                    cloud_name=settings.CLOUDINARY_STORAGE['CLOUD_NAME'],
                    api_key=settings.CLOUDINARY_STORAGE['API_KEY'],
                    api_secret=settings.CLOUDINARY_STORAGE['API_SECRET'],
                    secure=True
                )

                resultado = upload(
                    picture_file,
                    folder="noticias",
                    use_filename=True,
                    unique_filename=False
                )
                data['picture'] = resultado.get('secure_url')
            except Exception as e:
                return Response({"error": str(e)}, status=400)
        
        serializer = NoticiaSerializer(noticia, data=data, partial=True)
        if serializer.is_valid():
            serializer.save(updatedBy=request.user)
            return Response(serializer.data)

        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        if not es_admin_o_super(request.user):
            return Response({"detail": "No autorizado."}, status=status.HTTP_403_FORBIDDEN)

        noticia = get_object_or_404(Noticia, pk=pk)
        noticia.isActive = False
        noticia.deletedBy = request.user
        noticia.save()
        return Response({"detail": "Noticia desactivada correctamente."}, status=status.HTTP_204_NO_CONTENT)

class HabilitarNoticiaView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        if not es_admin_o_super(request.user):
            return Response({"detail": "No autorizado."}, status=status.HTTP_403_FORBIDDEN)

        noticia = get_object_or_404(Noticia, pk=pk, isActive=False)
        noticia.isActive = True
        noticia.updatedBy = request.user
        noticia.save()
        return Response({"detail": "Noticia habilitada correctamente."}, status=status.HTTP_200_OK)
    
