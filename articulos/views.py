import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.parsers import FormParser, JSONParser
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import get_object_or_404
from articulos.models import Articulo
from articulos.serializers import ArticuloSerializer

def es_admin_o_super(user):
    return user.is_authenticated and user.role in ['admin', 'super']

class CustomPageNumberPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class ArticuloView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [FormParser, JSONParser]

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def get(self, request, pk=None):
        if pk:
            articulo = get_object_or_404(Articulo, pk=pk)
            serializer = ArticuloSerializer(articulo)
            return Response(serializer.data)

        queryset = Articulo.objects.filter(isActive=True).order_by('-createdAt')

        title = request.query_params.get('title')
        tag = request.query_params.get('tag')

        if title:
            queryset = queryset.filter(title__icontains=title)
        if tag:
            queryset = queryset.filter(tags__icontains=tag)

        paginator = CustomPageNumberPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = ArticuloSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        if not es_admin_o_super(request.user):
            return Response({"detail": "No autorizado."}, status=status.HTTP_403_FORBIDDEN)

        data = request.data.copy()

        serializer = ArticuloSerializer(data=data)
        if serializer.is_valid():
            serializer.save(createdBy=request.user, isActive=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        if not es_admin_o_super(request.user):
            return Response({"detail": "No autorizado."}, status=status.HTTP_403_FORBIDDEN)

        articulo = get_object_or_404(Articulo, pk=pk)
        data = request.data.copy()

        tags_raw = data.get('tags')
        try:
            data['tags'] = json.loads(tags_raw) if tags_raw else []
        except Exception:
            return Response({"tags": ["Value must be valid JSON."]}, status=400)

        serializer = ArticuloSerializer(articulo, data=data, partial=True)
        if serializer.is_valid():
            serializer.save(updatedBy=request.user)
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        if not es_admin_o_super(request.user):
            return Response({"detail": "No autorizado."}, status=status.HTTP_403_FORBIDDEN)

        articulo = get_object_or_404(Articulo, pk=pk)
        articulo.isActive = False
        articulo.deletedBy = request.user
        articulo.save()
        return Response({"detail": "Artículo desactivado correctamente."}, status=status.HTTP_204_NO_CONTENT)

class HabilitarArticuloView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        if not es_admin_o_super(request.user):
            return Response({"detail": "No autorizado."}, status=status.HTTP_403_FORBIDDEN)

        articulo = get_object_or_404(Articulo, pk=pk, isActive=False)
        articulo.isActive = True
        articulo.updatedBy = request.user
        articulo.save()
        return Response({"detail": "Artículo habilitado correctamente."}, status=status.HTTP_200_OK)
    

