from swutils.encrypt import decrypt,encrypt

from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class EncryptedTextField(models.TextField):

    def from_db_value(self, value, expression, connection, context):
        if value is None:
            return value
        return decrypt(value, settings.SECRET_KEY.encode('utf-8'))

    def to_python(self, value):
        if value is None:
            return value
        return encrypt(value, settings.SECRET_KEY.encode('utf-8'))


def directory_path_root_key(instance, filename):
    return settings.ROOT_CRT_PATH + '/rootCA.key'


def directory_path_root_crt(instance, filename):
    return settings.ROOT_CRT_PATH + '/rootCA.crt'


class RootCrt(models.Model):
    key = EncryptedTextField()
    crt = EncryptedTextField()
    country = models.CharField(max_length=2)
    state = models.CharField(max_length=32)
    location = models.CharField(max_length=128)
    organization = models.CharField(max_length=256)
    organizational_unit_name = models.CharField(blank=True, null=True, max_length=256)
    email = models.EmailField(blank=True, null=True, max_length=128)


def directory_path_key(instance, filename):
    return '{cn}/{cn}.key'.format(cn=instance.cn)


def directory_path_crt(instance, filename):
    return '{cn}/{cn}.crt'.format(cn=instance.cn)


class SiteCrt(models.Model):
    key = EncryptedTextField()
    crt = EncryptedTextField()
    cn = models.CharField(max_length=256, unique=True)
    date_start = models.DateTimeField(auto_now_add=True)
    date_end = models.DateTimeField()
