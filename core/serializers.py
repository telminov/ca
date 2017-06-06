from rest_framework import serializers

from core import models
from core.utils import CA


class GenerateCrtSerializer(serializers.Serializer):
    cn = serializers.CharField(max_length=256)
    validity_period = serializers.DateField()

    def is_valid(self, raise_exception=False):
        bool_value = super(GenerateCrtSerializer, self).is_valid()
        if models.SiteCrt.objects.get(cn=self.initial_data['cn']):
            raise serializers.ValidationError('cn not unique')
        return bool_value

    def save(self):
        ca = CA()
        ca.generate_site_certificate(self.validated_data['cn'], self.validated_data['validity_period'])
