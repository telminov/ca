import os
from OpenSSL import crypto

from django.conf import settings

from ca import models

KEY_FILE = os.path.join(settings.ROOT_CRT_PATH, 'rootCA.key')
CERT_FILE = os.path.join(settings.ROOT_CRT_PATH, 'rootCA.crt')


def create_self_signed_cert_root(cleanned_data):
    k = crypto.PKey()
    k.generate_key(crypto.TYPE_RSA, 2048)

    cert = crypto.X509()

    cert.get_subject().C = cleanned_data['country']
    cert.get_subject().ST = cleanned_data['state']
    cert.get_subject().L = cleanned_data['location']
    cert.get_subject().O = cleanned_data['organization']
    if cleanned_data['organizational_unit_name']:
        cert.get_subject().OU = cleanned_data['organizational_unit_name']
    cert.get_subject().CN = cleanned_data['cn']
    if cleanned_data['email']:
        cert.get_subject().emailAddress = cleanned_data['email']

    cert.set_serial_number(1000)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(10 * 365 * 24 * 60 * 60)
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(k)
    cert.sign(k, 'sha1')

    key_path = os.path.join(settings.MEDIA_ROOT, KEY_FILE)
    cert_path = os.path.join(settings.MEDIA_ROOT, CERT_FILE)

    with open(cert_path, 'wb') as f:
        f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))

    with open(key_path, 'wb') as f:
        f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k))

    models.RootCrt.objects.create(
        key=KEY_FILE,
        crt=CERT_FILE
    )
