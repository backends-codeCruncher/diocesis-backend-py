import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from documentos.models import Documento
from documentos.serializers import DocumentoSerializer
from cloudinary.uploader import upload

def es_admin_o_super(user):
    return user.is_authenticated and user.role in ['admin', 'super']

class CustomPageNumberPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class DocumentoView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request, pk=None):
        if pk:
            documento = get_object_or_404(Documento, pk=pk)
            serializer = DocumentoSerializer(documento)
            return Response(serializer.data)

        queryset = Documento.objects.filter(isActive=True).order_by('-createdAt')

        title = request.query_params.get('title')
        tag = request.query_params.get('tag')
        tipo = request.query_params.get('type')

        if title:
            queryset = queryset.filter(title__icontains=title)
        if tag:
            queryset = queryset.filter(tags__icontains=tag)
        if tipo:
            queryset = queryset.filter(type=tipo)

        paginator = CustomPageNumberPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = DocumentoSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        if not es_admin_o_super(request.user):
            return Response({"detail": "No autorizado."}, status=status.HTTP_403_FORBIDDEN)

        data = request.data.copy()

        document_file = request.FILES.get('document')
        if document_file:
            resultado = upload(document_file, folder="documentos", resource_type="raw")
            data['document'] = resultado.get('secure_url')

        serializer = DocumentoSerializer(data=data)
        if serializer.is_valid():
            serializer.save(createdBy=request.user, isActive=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        if not es_admin_o_super(request.user):
            return Response({"detail": "No autorizado."}, status=status.HTTP_403_FORBIDDEN)

        documento = get_object_or_404(Documento, pk=pk)
        data = request.data.copy()

        document_file = request.FILES.get('document')
        if document_file:
            resultado = upload(document_file, folder="documentos", resource_type="raw")
            data['document'] = resultado.get('secure_url')

        tags_raw = data.get('tags')
        try:
            data['tags'] = json.loads(tags_raw) if tags_raw else []
        except Exception:
            return Response({"tags": ["Value must be valid JSON."]}, status=400)

        serializer = DocumentoSerializer(documento, data=data, partial=True)
        if serializer.is_valid():
            serializer.save(updatedBy=request.user)
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        if not es_admin_o_super(request.user):
            return Response({"detail": "No autorizado."}, status=status.HTTP_403_FORBIDDEN)

        documento = get_object_or_404(Documento, pk=pk)
        documento.isActive = False
        documento.deletedBy = request.user
        documento.save()
        return Response({"detail": "Documento desactivado correctamente."}, status=status.HTTP_204_NO_CONTENT)

class HabilitarDocumentoView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        if not es_admin_o_super(request.user):
            return Response({"detail": "No autorizado."}, status=status.HTTP_403_FORBIDDEN)

        documento = get_object_or_404(Documento, pk=pk, isActive=False)
        documento.isActive = True
        documento.updatedBy = request.user
        documento.save()
        return Response({"detail": "Documento habilitado correctamente."}, status=status.HTTP_200_OK)
    
