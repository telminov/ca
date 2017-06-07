import datetime
import os
from OpenSSL import crypto

from django.utils import timezone
from django.conf import settings

from core import models

CA_KEY_FILE = os.path.join(settings.ROOT_CRT_PATH, 'rootCA.key')
CA_CERT_FILE = os.path.join(settings.ROOT_CRT_PATH, 'rootCA.crt')


class CA:
    def generate_root_certificate(self, data, recreation=False):
        pkey = self.create_key_pair()
        validity_period = self.calculate_validity_period(data['validity_period'])
        if recreation:
            cert = self.create_cert_root(pkey, self.generate_subj_recreation_root_crt(), validity_period)
        else:
            cert = self.create_cert_root(pkey, self.generate_subj_root_crt(data), validity_period)
        self.write_cert_root(cert, pkey)
        if not recreation:
            self.create_model_root_crt(data)

    def generate_site_certificate(self, cn, validity_period, pk=None):
        pkey = self.create_key_pair()
        validity_period = self.calculate_validity_period(validity_period)
        cert = self.create_cert_site(pkey, self.generate_subj_site_crt(cn), validity_period)
        self.write_cert_site(cert, pkey, cn)
        if not pk:
            self.create_model_site_crt(cn, validity_period)
        else:
            self.recreation_site_crt(cn, pk, validity_period)

    def calculate_validity_period(self, date):
        now = datetime.datetime.now()
        validity_period = datetime.datetime.combine(date, now.time()) - now
        return int(validity_period.total_seconds())

    @staticmethod
    def generate_subj_site_crt(cn):
        root = models.RootCrt.objects.get()
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

    def generate_subj_recreation_root_crt(self):
        root = models.RootCrt.objects.get()
        options = {
            'C': root.country,
            'ST': root.state,
            'L': root.location,
            'O': root.organization,
            'OU': root.organizational_unit_name,
            'emailAddress': root.email,
        }
        return options

    def generate_subj_root_crt(self, data):
        options = {
            'C': data['country'],
            'ST': data['state'],
            'L': data['location'],
            'O': data['organization'],
            'OU': data['organizational_unit_name'],
            'CN': data['common_name'],
            'emailAddress': data['email'],
        }
        return options

    @staticmethod
    def create_key_pair():
        pkey = crypto.PKey()
        pkey.generate_key(crypto.TYPE_RSA, 2048)
        return pkey

    @staticmethod
    def create_cert_site(pkey, data, validity_period):
        root_crt = models.RootCrt.objects.get()
        with open(os.path.join(settings.MEDIA_ROOT, str(root_crt.crt))) as f:
            ca_cert = crypto.load_certificate(crypto.FILETYPE_PEM, f.read())

        with open(os.path.join(settings.MEDIA_ROOT, str(root_crt.key))) as f:
            ca_key = crypto.load_privatekey(crypto.FILETYPE_PEM, f.read())

        req = crypto.X509Req()
        subj = req.get_subject()

        for key, value in data.items():
            if value not in ['', None]:
                if key != 'validity_period':
                    print(subj, key, value)
                    setattr(subj, key, value)

        req.set_pubkey(pkey)
        req.sign(ca_key, 'sha256')

        cert = crypto.X509()
        cert.gmtime_adj_notBefore(0)
        cert.gmtime_adj_notAfter(validity_period)
        cert.set_issuer(ca_cert.get_subject())
        cert.set_subject(req.get_subject())
        cert.set_pubkey(req.get_pubkey())
        cert.sign(ca_key, 'sha256')
        return cert

    @staticmethod
    def create_cert_root(pkey, date, validity_period):
        cert = crypto.X509()
        subj = cert.get_subject()

        for key, value in date.items():
            if value != '':
                if key != 'validity_period':
                    setattr(subj, key, value)

        cert.gmtime_adj_notBefore(0)
        cert.gmtime_adj_notAfter(validity_period)
        cert.set_issuer(cert.get_subject())
        cert.set_pubkey(pkey)
        cert.sign(pkey, 'sha256')
        return cert

    @staticmethod
    def write_cert_root(cert, key):
        key_path = os.path.join(settings.MEDIA_ROOT, CA_KEY_FILE)
        cert_path = os.path.join(settings.MEDIA_ROOT, CA_CERT_FILE)

        if not os.path.exists(settings.MEDIA_ROOT):
            os.mkdir(settings.MEDIA_ROOT)

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
        root_crt = models.RootCrt.objects.create(
            key=CA_KEY_FILE,
            crt=CA_CERT_FILE,
            country=data['country'],
            state=data['state'],
            location=data['location'],
            organization=data['organization'],
            organizational_unit_name=data['organizational_unit_name'],
            email=data['email']
        )
        return root_crt

    @staticmethod
    def create_model_site_crt(cn, validity_period):
        site_crt = models.SiteCrt.objects.create(
            key=os.path.join(cn, cn + '.key'),
            crt=os.path.join(cn, cn + '.crt'),
            cn=cn,
            date_end=timezone.now() + datetime.timedelta(seconds=validity_period)
        )
        return site_crt

    @staticmethod
    def recreation_site_crt(cn, pk, validity_period):
        site_crt = models.SiteCrt.objects.filter(pk=pk).update(
            key=os.path.join(cn, cn + '.key'),
            crt=os.path.join(cn, cn + '.crt'),
            date_start=timezone.now(),
            date_end=timezone.now() + datetime.timedelta(seconds=validity_period)
        )
        return site_crt
