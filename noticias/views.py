import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
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
            return Response({"detail": "No autorizado."}, status=status.HTTP_403_FORBIDDEN)

        data = request.data.copy()
        picture_file = request.FILES.get('picture')
        if picture_file:
            resultado = upload(picture_file, folder="noticias")
            data['picture'] = resultado.get('secure_url')

        serializer = NoticiaSerializer(data=data)
        if serializer.is_valid():
            serializer.save(createdBy=request.user, isActive=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def put(self, request, pk):
        if not es_admin_o_super(request.user):
            return Response({"detail": "No autorizado."}, status=status.HTTP_403_FORBIDDEN)

        noticia = get_object_or_404(Noticia, pk=pk)
        data = request.data.copy()
        picture_file = request.FILES.get('picture')
        if picture_file:
            resultado = upload(picture_file, folder="noticias")
            data['picture'] = resultado.get('secure_url')

        if isinstance(data.get('tags'), str):
            data['tags'] = json.loads(data['tags'])

        serializer = NoticiaSerializer(noticia, data=data, partial=True)
        if serializer.is_valid():
            serializer.save(updatedBy=request.user)
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
    
