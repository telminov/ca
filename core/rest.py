from rest_framework import generics, authentication, permissions, renderers

from core import models
from core import serializers


class CreateCrt(generics.CreateAPIView):
    authentication_classes = (authentication.TokenAuthentication, authentication.SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = serializers.GenerateCrtSerializer
    queryset = models.SiteCrt.objects.all()


class GetCrt(generics.ListAPIView):
    authentication_classes = (authentication.TokenAuthentication, authentication.SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = serializers.GetCrtSerializer
    queryset = models.SiteCrt.objects.all()

    def get_queryset(self):
        queryset = models.SiteCrt.objects.all()
        cn = self.request.query_params.get('cn', None)
        if cn is not None:
            queryset = queryset.filter(cn=cn)
        return queryset
