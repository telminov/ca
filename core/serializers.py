from rest_framework import serializers

from core import models
from core.utils import CA


class GenerateCrtSerializer(serializers.ModelSerializer):
    validity_period = serializers.DateField()

    class Meta:
        model = models.SiteCrt
        fields = ['cn', 'validity_period']

    def save(self):
        ca = CA()
        ca.generate_site_certificate(self.validated_data['cn'], self.validated_data['validity_period'])


class GetCrtSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SiteCrt
        fields = ['cn', 'crt']

    def to_representation(self, instance):
        dict_ret = super().to_representation(instance)
        crt = models.SiteCrt.objects.get(cn=dict_ret['cn']).crt.read()
        dict_ret['crt'] = crt
        return dict_ret
