from rest_framework import generics, authentication, permissions

from core import models
from core import serializers


class SiteCrtCreate(generics.CreateAPIView):
    authentication_classes = (authentication.TokenAuthentication, authentication.SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = serializers.SiteCrtCreate
    queryset = models.SiteCrt.objects.all()


class SiteCrtList(generics.ListAPIView):
    authentication_classes = (authentication.TokenAuthentication, authentication.SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = serializers.SiteCrt
    queryset = models.SiteCrt.objects.all()
    filter_fields = ('cn', )
