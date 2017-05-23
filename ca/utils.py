import datetime
import os
from OpenSSL import crypto

from django.utils import timezone
from django.conf import settings

from ca import models

CA_KEY_FILE = os.path.join(settings.ROOT_CRT_PATH, 'rootCA.key')
CA_CERT_FILE = os.path.join(settings.ROOT_CRT_PATH, 'rootCA.crt')


# class CA:
#     def __init__(self, **data):
#         self.C = data.get('country')
#         self.ST = data.get('state')
#         self.L = data.get('location')
#         self.O = data.get('organization')
#         self.OU = data.get('organizational_unit_name')
#         self.CN = data.get('cn')
#         self.emailAddress = data.get('email')
#
#
#     def make_key_pair(self, key_type=crypto.TYPE_RSA, bits=2048):
#         pkey = crypto.PKey()
#         pkey.generate_key(key_type, bits)
#         return pkey
#
#     def make_root_cert(self, pkey, notBefore=0, notAfter= 5 * 365 * 24 * 60 * 60):
#         cert = crypto.X509()
#         cert_subj = cert.get_subject()
#
#         cert_subj.C = self.C
#         cert_subj.ST = self.ST
#         cert_subj.L = self.L
#         cert_subj.O = self.O
#         if self.OU:
#             cert_subj.OU = self.OU
#         cert_subj.CN = '127.0.0.1'
#         if self.emailAddress:
#             cert_subj.emailAddress = self.emailAddress
#
#         cert.set_serial_number(1000)
#         cert.gmtime_adj_notBefore(notBefore)
#         cert.gmtime_adj_notAfter(notAfter)
#         cert.set_issuer(cert_subj)
#         cert.set_pubkey(pkey)
#         cert.sign(pkey, 'sha256')
#
#         with open(os.path.join(settings.MEDIA_ROOT, CA_KEY_FILE), 'wb') as f:
#             f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, pkey))
#
#         with open(os.path.join(settings.MEDIA_ROOT, CA_CERT_FILE), 'wb') as f:
#             f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
#
#     def make_req_site(self, pkey, ca_key, cn='127.0.0.1'):
#         req = crypto.X509Req()
#
#         req.get_subject().C = self.C
#         req.get_subject().ST = self.ST
#         req.get_subject().L = self.L
#         req.get_subject().O = self.O
#         if self.OU:
#             req.get_subject().OU = self.OU
#         req.get_subject().CN = cn
#         if self.emailAddress:
#             req.get_subject().emailAddress = self.emailAddress
#
#         req.set_pubkey(pkey)
#         req.sign(ca_key, 'sha256')
#         return req
#
#     def make_cert_site(self, req, issuerCert, issuerKey, cn, key):
#         cert = crypto.X509()
#         cert.set_serial_number(1000)
#         cert.gmtime_adj_notBefore(0)
#         cert.gmtime_adj_notAfter(5 * 365 * 24 * 60 * 60)
#         cert.set_issuer(issuerCert.get_subject())
#         cert.set_subject(req.get_subject())
#         cert.set_pubkey(req.get_pubkey())
#         cert.sign(issuerKey, 'sha256')
#
#         with open(os.path.join(settings.MEDIA_ROOT, cn, cn + '.crt'), 'wb') as f:
#             f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
#
#         with open(os.path.join(settings.MEDIA_ROOT, cn, cn + '.key'), 'wb') as f:
#             f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key))

class CA:

    def generate_root_certificate(self, data):
        pkey = self.create_key_pair()
        cert = self.create_cert_root(pkey, data)
        self.write_cert_root(cert, pkey)
        self.create_model_root_crt(data)

    def generate_site_certificate(self, cn):
        pkey = self.create_key_pair()
        cert = self.create_cert_site(pkey, self.generate_dict(cn))
        self.write_cert_site(cert, pkey, cn)
        self.create_model_site_crt(cn)

    @staticmethod
    def generate_dict(cn):
        root = models.RootCrt.objects.first()
        options = {
            'C': root.country,
            'ST': root.state,
            'L': root.location,
            'O': root.organization,
            'OU': root.organizational_unit_name,
            'CN': cn,
            'emailAddress': root.email,
        }
        return options

    @staticmethod
    def create_key_pair():
        pkey = crypto.PKey()
        pkey.generate_key(crypto.TYPE_RSA, 2048)
        return pkey

    # def create_cert_req(self, pkey, **data):
    #     with open(os.path.join(settings.MEDIA_ROOT, CA_KEY_FILE)) as f:
    #         ca_key = crypto.load_privatekey(crypto.FILETYPE_PEM, f.read())
    #
    #     req = crypto.X509Req()
    #     subj = req.get_subject()
    #
    #     for key, value in data.items():
    #         if value != '':
    #             setattr(subj, key, value)
    #
    #     req.set_pubkey(pkey)
    #     req.sign(ca_key, 'sha256')
    #     return req

    @staticmethod
    def create_cert_site(pkey, data):
        with open(os.path.join(settings.MEDIA_ROOT, CA_CERT_FILE)) as f:
            ca_cert = crypto.load_certificate(crypto.FILETYPE_PEM, f.read())

        with open(os.path.join(settings.MEDIA_ROOT, CA_KEY_FILE)) as f:
            ca_key = crypto.load_privatekey(crypto.FILETYPE_PEM, f.read())

        req = crypto.X509Req()
        subj = req.get_subject()

        for key, value in data.items():
            if value != '':
                setattr(subj, key, value)

        req.set_pubkey(pkey)
        req.sign(ca_key, 'sha256')

        cert = crypto.X509()
        cert.gmtime_adj_notBefore(0)
        cert.gmtime_adj_notAfter(5 * 365 * 24 * 60 * 60)
        cert.set_issuer(ca_cert.get_subject())
        cert.set_subject(req.get_subject())
        cert.set_pubkey(req.get_pubkey())
        cert.sign(ca_key, 'sha256')
        return cert

    @staticmethod
    def create_cert_root(pkey, date):
        cert = crypto.X509()
        subj = cert.get_subject()

        for key, value in date.items():
            if value != '':
                setattr(subj, key, value)

        cert.gmtime_adj_notBefore(0)
        cert.gmtime_adj_notAfter(5 * 365 * 24 * 60 * 60)
        cert.set_issuer(cert.get_subject())
        cert.set_pubkey(pkey)
        cert.sign(pkey, 'sha256')
        return cert

    @staticmethod
    def write_cert_root(cert, key):
        key_path = os.path.join(settings.MEDIA_ROOT, CA_KEY_FILE)
        cert_path = os.path.join(settings.MEDIA_ROOT, CA_CERT_FILE)

        if not os.path.exists(os.path.join(settings.MEDIA_ROOT, settings.ROOT_CRT_PATH)):
            os.mkdir(os.path.join(settings.MEDIA_ROOT, settings.ROOT_CRT_PATH))

        with open(cert_path, 'wb') as f:
            f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))

        with open(key_path, 'wb') as f:
            f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key))

    @staticmethod
    def write_cert_site(cert, key, cn):
        if not os.path.exists(os.path.join(settings.MEDIA_ROOT, cn)):
            os.mkdir(os.path.join(settings.MEDIA_ROOT, cn))

        with open(os.path.join(settings.MEDIA_ROOT, cn, cn + '.crt'), 'wb') as f:
            f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))

        with open(os.path.join(settings.MEDIA_ROOT, cn, cn + '.key'), 'wb') as f:
            f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key))

    @staticmethod
    def create_model_root_crt(data):
        models.RootCrt.objects.create(
            key=CA_KEY_FILE,
            crt=CA_CERT_FILE,
            country=data['C'],
            state=data['ST'],
            location=data['L'],
            organization=data['O'],
            organizational_unit_name=data['OU'],
            email=data['emailAddress']
        )

    @staticmethod
    def create_model_site_crt(cn):
        models.SiteCrt.objects.create(
            key=os.path.join(cn, cn + '.key'),
            crt=os.path.join(cn, cn + '.crt'),
            cn=cn,
            date_end=timezone.now() + datetime.timedelta(seconds=5 * 365 * 24 * 60 * 60)
        )


# def create_self_signed_cert_root(cleanned_data):
#     k = crypto.PKey()
#     k.generate_key(crypto.TYPE_RSA, 2048)
#
#     cert = crypto.X509()
#
#     cert.get_subject().C = cleanned_data['country']
#     cert.get_subject().ST = cleanned_data['state']
#     cert.get_subject().L = cleanned_data['location']
#     cert.get_subject().O = cleanned_data['organization']
#     if cleanned_data['organizational_unit_name']:
#         cert.get_subject().OU = cleanned_data['organizational_unit_name']
#     cert.get_subject().CN = cleanned_data['cn']
#     if cleanned_data['email']:
#         cert.get_subject().emailAddress = cleanned_data['email']
#
#     cert.set_serial_number(1000)
#     cert.gmtime_adj_notBefore(0)
#     cert.gmtime_adj_notAfter(5 * 365 * 24 * 60 * 60)
#     cert.set_issuer(cert.get_subject())
#     cert.set_pubkey(k)
#     cert.sign(k, 'sha256')
#
#     key_path = os.path.join(settings.MEDIA_ROOT, CA_KEY_FILE)
#     cert_path = os.path.join(settings.MEDIA_ROOT, CA_CERT_FILE)
#
#     if not os.path.exists(os.path.join(settings.MEDIA_ROOT, settings.ROOT_CRT_PATH)):
#         os.mkdir(os.path.join(settings.MEDIA_ROOT, settings.ROOT_CRT_PATH))
#
#     with open(cert_path, 'wb') as f:
#         f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
#
#     with open(key_path, 'wb') as f:
#         f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k))
#
#     models.RootCrt.objects.create(
#         key=CA_KEY_FILE,
#         crt=CA_CERT_FILE,
#         country=cleanned_data['country'],
#         state=cleanned_data['state'],
#         location=cleanned_data['location'],
#         organization=cleanned_data['organization'],
#         organizational_unit_name=cleanned_data['organizational_unit_name'],
#         email=cleanned_data['email']
#     )
#
# def create_signed_cert(cn):
#     ca_cert = crypto.load_certificate(crypto.FILETYPE_PEM, open(os.path.join(settings.MEDIA_ROOT, CA_CERT_FILE)).read())
#
#     ca_key = crypto.load_privatekey(crypto.FILETYPE_PEM, open(os.path.join(settings.MEDIA_ROOT, CA_KEY_FILE)).read())
#
#     k = crypto.PKey()
#     k.generate_key(crypto.TYPE_RSA, 2048)
#
#     cert_req = crypto.X509Req()
#
#     cert_req.get_subject().C = models.RootCrt.objects.first().country
#     cert_req.get_subject().ST = models.RootCrt.objects.first().state
#     cert_req.get_subject().L = models.RootCrt.objects.first().location
#     cert_req.get_subject().O = models.RootCrt.objects.first().organization
#     if models.RootCrt.objects.first().organizational_unit_name:
#         cert_req.get_subject().OU = models.RootCrt.objects.first().organizational_unit_name
#     cert_req.get_subject().CN = cn
#     if models.RootCrt.objects.first().email:
#         cert_req.get_subject().emailAddress = models.RootCrt.objects.first().email
#
#     cert_req.set_pubkey(k)
#     cert_req.sign(ca_key, 'sha256')
#
#     cert = crypto.X509()
#     cert.gmtime_adj_notBefore(0)
#     cert.gmtime_adj_notAfter(5 * 365 * 24 * 60 * 60)
#     cert.set_issuer(ca_cert.get_subject())
#     cert.set_subject(cert_req.get_subject())
#     cert.set_pubkey(cert_req.get_pubkey())
#     cert.sign(ca_key, 'sha256')
#
#     if not os.path.exists(os.path.join(settings.MEDIA_ROOT, cn)):
#         os.mkdir(os.path.join(settings.MEDIA_ROOT, cn))
#
#     with open(os.path.join(settings.MEDIA_ROOT, cn, cn + '.crt'), 'wb') as f:
#         f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
#
#     with open(os.path.join(settings.MEDIA_ROOT, cn, cn + '.key'), 'wb') as f:
#         f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k))
#
#     models.SiteCrt.objects.create(
#         key=os.path.join(cn, cn + '.key'),
#         crt=os.path.join(cn, cn + '.crt'),
#         cn=cn,
#         date_end=timezone.now() + datetime.timedelta(seconds=5 * 365 * 24 * 60 * 60)
#     )
