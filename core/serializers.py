import re

from rest_framework import serializers

from core import models
from core.utils import Ca


class SiteCrtCreate(serializers.ModelSerializer):
    validity_period = serializers.DateField()

    class Meta:
        model = models.SiteCrt
        fields = ['cn', 'validity_period']

    def save(self):
        ValidIpAddressRegex = r"^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$"
        ca = Ca()
        if re.findall(ValidIpAddressRegex, self.validated_data['cn']):
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
