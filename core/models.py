from django.db import models
from django.conf import settings


class RootCrt(models.Model):
    key = models.FileField(upload_to=settings.ROOT_CRT_PATH)
    crt = models.FileField(upload_to=settings.ROOT_CRT_PATH)
    country = models.CharField(max_length=2)
    state = models.CharField(max_length=32)
    location = models.CharField(max_length=128)
    organization = models.CharField(max_length=256)
    organizational_unit_name = models.CharField(blank=True, null=True, max_length=256)
    email = models.EmailField(blank=True, null=True, max_length=128)


class SiteCrt(models.Model):
    key = models.FileField(upload_to=lambda instance, filename: '{cn}/{filename}'.format(cn=instance.cn, filename=filename))
    crt = models.FileField(upload_to=lambda instance, filename: '{cn}/{filename}'.format(cn=instance.cn, filename=filename))
    cn = models.CharField(max_length=256, unique=True)
    date_start = models.DateTimeField(auto_now_add=True)
    date_end = models.DateTimeField()
