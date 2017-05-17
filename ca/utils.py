import os
from OpenSSL import crypto

from django.conf import settings

from ca import models

KEY_FILE = os.path.join(settings.ROOT_CA, 'rootCA.key')
CERT_FILE = os.path.join(settings.ROOT_CA, 'rootCA.crt')


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

    with open(CERT_FILE, 'wb') as f:
        f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))

    with open(KEY_FILE, 'wb') as f:
        f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k))

    path_key, name_key = os.path.join(KEY_FILE)
    path_crt, name_crt = os.path.join(CERT_FILE)

    models.RootCrt.objects.create(
        key=os.path.join(os.path.dirname(path_key), name_key),
        crt=os.path.join(os.path.dirname(path_crt), name_crt)
    )
