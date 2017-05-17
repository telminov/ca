from django.db import models
from django.conf import settings


class RootCrt(models.Model):
    key = models.FileField(upload_to=settings.ROOT_CRT_PATH)
    crt = models.FileField(upload_to=settings.ROOT_CRT_PATH)
