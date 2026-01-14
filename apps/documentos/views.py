import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import get_object_or_404
from django.conf import settings
import cloudinary.uploader
from apps.documentos.models import Documento
from apps.documentos.serializers import DocumentoSerializer
from cloudinary.uploader import upload
from django.db.models.expressions import RawSQL

def es_admin_o_super(user):
    return user.is_authenticated and user.role in ['admin', 'super']

class CustomPageNumberPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class DocumentoView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request, pk=None):
        if pk:
            documento = get_object_or_404(Documento, pk=pk)
            serializer = DocumentoSerializer(documento)
            return Response(serializer.data)

        queryset = Documento.objects.all().order_by('-createdAt')

        title = request.query_params.get('title')
        tag = request.query_params.get('tags')
        tipo = request.query_params.get('type')
        is_active_param = request.query_params.get('isActive')

        if is_active_param is None or is_active_param == '':
            is_active = None
        elif is_active_param.lower() == 'true':
            is_active = True
        elif is_active_param.lower() == 'false':
            is_active = False
        else:
            is_active = None

        if title:
            queryset = queryset.filter(title__icontains=title)

        if tag:
            tag = tag.strip()
            if tag:
                queryset = queryset.extra(
                    where=[
                        """
                        EXISTS (
                            SELECT 1
                            FROM jsonb_array_elements_text(
                                COALESCE(tags::jsonb, '[]'::jsonb)
                            ) AS t(value)
                            WHERE t.value ILIKE %s
                        )
                        """
                    ],
                    params=[f"%{tag}%"]
                )

        if tipo:
            queryset = queryset.filter(type=tipo)

        if is_active is None:
            pass
        elif is_active is True:
            queryset = queryset.filter(isActive=True)
        elif is_active is False:
            queryset = queryset.filter(isActive=False)

        paginator = CustomPageNumberPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = DocumentoSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


    def post(self, request):
        if not es_admin_o_super(request.user):
            return Response({"detail": "No autorizado."}, status=403)

        data = request.data.copy()
        document_file = request.FILES.get('document')

        if document_file:
            try:
                cloudinary.config(
                    cloud_name=settings.CLOUDINARY_STORAGE['CLOUD_NAME'],
                    api_key=settings.CLOUDINARY_STORAGE['API_KEY'],
                    api_secret=settings.CLOUDINARY_STORAGE['API_SECRET'],
                    secure=True
                )
                resultado = upload(
                    document_file,
                    folder="documentos",
                    resource_type="raw",
                    use_filename=True,
                    unique_filename=False
                )
                data['document'] = resultado.get('secure_url')
            except Exception as e:
                return Response({"error": str(e)}, status=400)

        serializer = DocumentoSerializer(data=data)
        if serializer.is_valid():
            serializer.save(createdBy=request.user, isActive=True)
            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)

    def put(self, request, pk):
        if not es_admin_o_super(request.user):
            return Response({"detail": "No autorizado."}, status=status.HTTP_403_FORBIDDEN)

        documento = get_object_or_404(Documento, pk=pk)
        data = request.data.copy()

        document_file = request.FILES.get('document')
        if document_file:
            resultado = upload(document_file, folder="documentos", resource_type="raw")
            data['document'] = resultado.get('secure_url')

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
    
