from rest_framework import generics, views, viewsets

from core import models
from core import serializers


class CreateCrt(generics.CreateAPIView):
    serializer_class = serializers.GenerateCrtSerializer
    queryset = models.SiteCrt.objects.all()
