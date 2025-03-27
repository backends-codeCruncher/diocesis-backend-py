from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from padres.models import Padre
from padres.serializers import PadreSerializer

class PadreView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request, pk=None):
        if pk:
            padre = get_object_or_404(Padre, pk=pk)
            serializer = PadreSerializer(padre)
            return Response(serializer.data)

        padres = Padre.objects.all().order_by('lastName')
        serializer = PadreSerializer(padres, many=True)
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
    
