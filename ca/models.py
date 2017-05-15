from django.db import models


class RootCrt(models.Model):
    key = models.FileField(upload_to='root/')
    crt = models.FileField(upload_to='root/')
