from OpenSSL import crypto
from django.conf import settings

from ca import models

KEY_FILE = '/root/rootCA.key'
CERT_FILE = '/root/rootCA.crt'


def create_self_signed_cert_root(cleanned_data):
    k = crypto.PKey()
    k.generate_key(crypto.TYPE_RSA, 2048)

    cert = crypto.X509()
    cert.get_subject().C = cleanned_data['Country']
    cert.get_subject().ST = cleanned_data['State']
    cert.get_subject().L = cleanned_data['Location']
    cert.get_subject().O = cleanned_data['Organization']
    if cleanned_data['Organizational_Unit_Name']:
        cert.get_subject().OU = cleanned_data['Organizational_Unit_Name']
    cert.get_subject().CN = cleanned_data['CN']
    if cleanned_data['email']:
        cert.get_subject().emailAddress = cleanned_data['email']
    cert.set_serial_number(1000)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(10 * 365 * 24 * 60 * 60)
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(k)
    cert.sign(k, 'sha1')

    with open(settings.MEDIA_ROOT + CERT_FILE, 'wb') as f:
        f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))

    with open(settings.MEDIA_ROOT + KEY_FILE, 'wb') as f:
        f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k))

    models.RootCrt.objects.create(
        key=KEY_FILE,
        crt=CERT_FILE
    )
