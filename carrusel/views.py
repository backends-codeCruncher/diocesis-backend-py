from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
import cloudinary.uploader

from .models import Carrusel
from .serializers import CarruselSerializer


# Permiso personalizado
def es_admin_o_super(user):
    return user.role in ['admin', 'super']


class CarruselView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        """
        Lista todos los elementos del carrusel
        """
        carruseles = Carrusel.objects.all().order_by('-createdAt')
        serializer = CarruselSerializer(carruseles, many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        Crea un nuevo carrusel (imagen o video). Solo admin o super pueden usarlo.
        """
        if not es_admin_o_super(request.user):
            return Response({"detail": "No tienes permisos para crear elementos del carrusel."}, status=403)

        file = request.FILES.get('url')
        is_image = request.data.get('isImage', 'true').lower() == 'true'

        if not file:
            return Response({"error": "Debes proporcionar un archivo en el campo 'url'."}, status=400)

        try:
            folder = 'carrusel/imagenes' if is_image else 'carrusel/videos'
            resource_type = 'image' if is_image else 'video'

            upload_result = cloudinary.uploader.upload(
                file,
                resource_type=resource_type,
                folder=folder,
                use_filename=True,
                unique_filename=False
            )

            carrusel = Carrusel.objects.create(
                url=upload_result['secure_url'],
                isImage=is_image,
                createdBy=request.user
            )

            serializer = CarruselSerializer(carrusel)
            return Response(serializer.data, status=201)

        except Exception as e:
            return Response({"error": str(e)}, status=400)

    def put(self, request, pk):
        """
        Actualiza un carrusel existente. Puedes cambiar el archivo o el valor de isImage.
        """
        if not es_admin_o_super(request.user):
            return Response({"detail": "No tienes permisos para modificar elementos del carrusel."}, status=403)

        carrusel = get_object_or_404(Carrusel, pk=pk)
        file = request.FILES.get('url', None)
        is_image = request.data.get('isImage', str(carrusel.isImage)).lower() == 'true'

        try:
            if file:
                folder = 'carrusel/imagenes' if is_image else 'carrusel/videos'
                resource_type = 'image' if is_image else 'video'

                upload_result = cloudinary.uploader.upload(
                    file,
                    resource_type=resource_type,
                    folder=folder,
                    use_filename=True,
                    unique_filename=False
                )
                carrusel.url = upload_result['secure_url']

            carrusel.isImage = is_image
            carrusel.save()

            serializer = CarruselSerializer(carrusel)
            return Response(serializer.data)

        except Exception as e:
            return Response({"error": str(e)}, status=400)

    def delete(self, request, pk):
        """
        Elimina un elemento del carrusel (solo admin o super).
        """
        if not es_admin_o_super(request.user):
            return Response({"detail": "No tienes permisos para eliminar elementos del carrusel."}, status=403)

        carrusel = get_object_or_404(Carrusel, pk=pk)
        carrusel.delete()
        return Response({"detail": "Elemento eliminado correctamente."}, status=204)