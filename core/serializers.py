from rest_framework import serializers

from core import models
from core.utils import Ca


class SiteCrtCreate(serializers.ModelSerializer):
    validity_period = serializers.DateField()

    class Meta:
        model = models.SiteCrt
        fields = ['cn', 'validity_period']

    def save(self):
        ca = Ca()
        if ca.get_type_alt_names(self.validated_data['cn']):
            ca.generate_site_crt(self.validated_data['cn'], self.validated_data['validity_period'], alt_name='IP')
        else:
            ca.generate_site_crt(self.validated_data['cn'], self.validated_data['validity_period'])


class SiteCrt(serializers.ModelSerializer):
    crt = serializers.SerializerMethodField()

    class Meta:
        model = models.SiteCrt
        fields = ['cn', 'crt']

    @staticmethod
    def get_crt(obj):
        return obj.crt.read()
